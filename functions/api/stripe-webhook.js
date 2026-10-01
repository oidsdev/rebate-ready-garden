// POST /api/stripe-webhook — Stripe event receiver.
// Verifies the Stripe-Signature header (HMAC-SHA256, see _shared.js).
// On checkout.session.completed (paid): emails the buyer their HMAC-signed
// 72h download links via Resend. This is the email fallback — the success
// page already serves the same links directly via /api/order, so a buyer
// who closes the tab still gets their products by email.
//
// Idempotency: durable, via the Checkout Session's own metadata
// (email_sent=1 written with the restricted key after a successful send),
// plus an in-memory Set as a fast path. The in-memory mark is only set for
// terminally handled events — a failed or never-attempted send stays
// retryable, so a Stripe retry always re-attempts the email until the
// durable flag exists. A retried Stripe delivery that arrives after a
// completed send returns {duplicate:true} and sends nothing.
//
// Required Pages secrets: STRIPE_SECRET_KEY, STRIPE_WEBHOOK_SECRET,
// DOWNLOAD_SECRET, RESEND_API_KEY. Optional: EMAIL_FROM
// (default "Rebate-Ready Garden <orders@rebatereadygarden.com>").
import { CATALOG } from "../_catalog.js";
import {
  verifyStripeSignature,
  signDownloadToken,
  json,
} from "../_shared.js";

const seen = new Set();
const MAX_SEEN = 5000;

// Fast-path duplicate check. IMPORTANT: an event id is only added to `seen`
// once it is terminally handled (sent, or a no-op). A failed email send or a
// send that never happened (missing RESEND_API_KEY) must NOT be marked, or a
// Stripe retry landing on this isolate would be swallowed as a duplicate
// before the durable email_sent marker exists. The durable guard is the
// Checkout Session metadata flag; this set is only a shortcut.
function isSeen(eventId) {
  return !!eventId && seen.has(eventId);
}
function markSeen(eventId) {
  if (!eventId) return;
  seen.add(eventId);
  if (seen.size > MAX_SEEN) seen.delete(seen.values().next().value);
}

async function stripeGet(secret, path) {
  const r = await fetch(`https://api.stripe.com/v1${path}`, {
    headers: { Authorization: `Bearer ${secret}` },
  });
  const data = await r.json().catch(() => ({}));
  return { ok: r.ok, status: r.status, data };
}

async function stripePostForm(secret, path, params) {
  const body = new URLSearchParams(params);
  const r = await fetch(`https://api.stripe.com/v1${path}`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${secret}`,
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: body.toString(),
  });
  const data = await r.json().catch(() => ({}));
  return { ok: r.ok, status: r.status, data };
}

function esc(s) {
  return String(s)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function buildEmail({ email, items, origin }) {
  const rows = items
    .map(
      (it) => `
      <tr>
        <td style="padding:12px 0;border-bottom:1px solid #e5e0d5;">
          <div style="font-weight:600;color:#2d4a22;">${esc(it.name)}</div>
          <div style="margin-top:6px;">
            <a href="${esc(it.url)}" style="display:inline-block;background:#2d4a22;color:#ffffff;text-decoration:none;padding:10px 18px;border-radius:6px;font-weight:600;">Download your plan</a>
          </div>
          <div style="font-size:12px;color:#777;margin-top:6px;word-break:break-all;">Or copy this link:<br>${esc(it.url)}</div>
        </td>
      </tr>`
    )
    .join("");

  const html = `<!doctype html>
<html><body style="font-family:Georgia,serif;background:#f7f4ec;margin:0;padding:24px;color:#333;">
<div style="max-width:560px;margin:0 auto;background:#ffffff;border-radius:10px;padding:32px;">
<h1 style="color:#2d4a22;font-size:22px;margin:0 0 8px;">Your garden plans are ready</h1>
<p>Thanks for your order. Your download links are below — they work for the next 72 hours, and you can re-download any time within that window.</p>
<table style="width:100%;border-collapse:collapse;margin:16px 0;">${rows}</table>
<p style="font-size:13px;color:#666;">What's inside each plan: planting layout, rebate rules for your program, compliance checklist, plant list, and the official application link for your county.</p>
<p style="font-size:13px;color:#666;">Questions? Reply to this email. Full terms: <a href="${esc(origin)}/terms.html">${esc(origin)}/terms.html</a></p>
<p style="font-size:12px;color:#999;margin-top:24px;">Rebate-Ready Garden · Orbital Desk LLC<br>This email confirms your purchase. Keep your Stripe receipt for your records.</p>
</div></body></html>`;

  const text = [
    "Your Rebate-Ready Garden plans are ready.",
    "",
    ...items.flatMap((it) => [it.name, it.url, ""]),
    "Links work for 72 hours.",
    `Terms: ${origin}/terms.html`,
    "Questions? Just reply to this email.",
    "Rebate-Ready Garden · Orbital Desk LLC",
  ].join("\n");

  return { html, text };
}

async function sendViaResend({ apiKey, from, to, subject, html, text }) {
  const r = await fetch("https://api.resend.com/emails", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${apiKey}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ from, to, subject, html, text }),
  });
  const data = await r.json().catch(() => ({}));
  return { ok: r.ok, status: r.status, data };
}

export async function onRequestPost({ request, env }) {
  const v = await verifyStripeSignature(request, env.STRIPE_WEBHOOK_SECRET);
  if (!v.ok) return json({ error: v.error }, v.status);
  const event = v.event;
  const type = event.type || "";
  const obj = (event.data && event.data.object) || {};
  const eventId = String(event.id || "");

  if (isSeen(eventId)) return json({ received: true, duplicate: true });

  if (type !== "checkout.session.completed") {
    markSeen(eventId);
    return json({ received: true, ignored: type });
  }

  const sessionId = String(obj.id || "");
  if (!sessionId || !env.STRIPE_SECRET_KEY || !env.DOWNLOAD_SECRET) {
    console.log("webhook: misconfigured (missing session id or secrets)");
    return json({ error: "webhook_misconfigured" }, 500);
  }

  // Re-fetch the session: authoritative payment status + durable idempotency flag.
  const sess = await stripeGet(
    env.STRIPE_SECRET_KEY,
    `/checkout/sessions/${encodeURIComponent(sessionId)}`
  );
  if (!sess.ok) {
    console.log(`webhook: session fetch failed (${sess.status}) for ${sessionId}`);
    return json({ error: "session_lookup_failed" }, 502);
  }
  const s = sess.data || {};
  if ((s.payment_status || "") !== "paid") {
    markSeen(eventId); // terminal: a later paid state arrives as a new event
    return json({ received: true, ignored: "unpaid" });
  }
  const meta = s.metadata || {};
  if (meta.email_sent === "1") {
    markSeen(eventId);
    return json({ received: true, duplicate: true });
  }

  const sku = String(meta.sku || "");
  const email = String(
    s.customer_email || s.customer_details?.email || s.client_reference_id || ""
  ).trim().toLowerCase();
  const item = CATALOG.find((p) => p.sku === sku);
  if (!item || !email) {
    console.log(`webhook: ignored (sku=${sku} email=${email ? "set" : "missing"})`);
    markSeen(eventId); // terminal: reprocessing could not succeed either
    return json({ received: true });
  }

  const skus = item.bundle_of || [item.sku];
  const origin = new URL(request.url).origin;
  const items = [];
  for (const ps of skus) {
    const prod = CATALOG.find((p) => p.sku === ps);
    if (!prod) continue;
    const token = await signDownloadToken(env.DOWNLOAD_SECRET, ps, email, 72);
    items.push({
      sku: ps,
      name: prod.name,
      url: `${origin}/api/download?token=${token}`,
    });
  }
  if (!items.length) {
    markSeen(eventId); // terminal: nothing to email
    return json({ received: true, ignored: "no_products" });
  }

  if (!env.RESEND_API_KEY) {
    // Config not finished: don't fail the webhook (Stripe would retry
    // forever), and do NOT mark seen — once the key is wired, a retried
    // delivery must still send. Log loudly so the operator wires the key.
    console.log(`webhook: RESEND_API_KEY missing — email NOT sent to ${email} (sku=${sku}). Wire the secret.`);
    return json({ received: true, email_pending: true, email, sku });
  }

  const from =
    env.EMAIL_FROM || "Rebate-Ready Garden <orders@rebatereadygarden.com>";
  const { html, text } = buildEmail({ email, items, origin });
  const sent = await sendViaResend({
    apiKey: env.RESEND_API_KEY,
    from,
    to: email,
    subject: "Your Rebate-Ready Garden plans are ready",
    html,
    text,
  });
  if (!sent.ok) {
    console.log(`webhook: Resend failed (${sent.status}) for ${email}: ${JSON.stringify(sent.data).slice(0, 200)}`);
    // Return 502 so Stripe retries; do NOT mark seen — the retry must
    // re-attempt the send. The durable email_sent flag is still unset.
    return json({ error: "email_failed", detail: sent.data }, 502);
  }

  // Durable idempotency mark, then the fast-path mark.
  const marked = await stripePostForm(env.STRIPE_SECRET_KEY,
    `/checkout/sessions/${encodeURIComponent(sessionId)}`,
    { "metadata[email_sent]": "1" }
  );
  if (!marked.ok) {
    console.log(`webhook: WARNING — email sent to ${email} but email_sent marker write failed (${marked.status}). A retried delivery may re-send.`);
  }
  markSeen(eventId);

  console.log(`webhook: emailed ${items.length} link(s) to ${email} (sku=${sku}, resend=${sent.data.id || "ok"})`);
  return json({ received: true, emailed: true, email, items: items.length });
}
