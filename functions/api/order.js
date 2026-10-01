// GET /api/order?session_id=cs_... — verify a paid Checkout Session and
// return the buyer's signed 72h download links. This is what powers the
// success page: the buyer gets their files immediately after payment,
// with no email delivery required.
// Security: the session ID is an unguessable bearer token; we re-fetch the
// session from Stripe with the secret key and require payment_status=paid.
import { CATALOG } from "../_catalog.js";
import { signDownloadToken, json } from "../_shared.js";

export async function onRequestGet({ request, env }) {
  const sessionId = new URL(request.url).searchParams.get("session_id") || "";
  if (!/^cs_(live|test)_[A-Za-z0-9]+$/.test(sessionId)) {
    return json({ error: "bad_session", message: "We could not find that order." }, 400);
  }
  const secret = env.STRIPE_SECRET_KEY;
  if (!secret || !env.DOWNLOAD_SECRET) {
    return json({ error: "not_configured", message: "Order lookup is not configured yet." }, 503);
  }

  const r = await fetch(
    `https://api.stripe.com/v1/checkout/sessions/${encodeURIComponent(sessionId)}`,
    { headers: { Authorization: "Basic " + btoa(secret + ":") } }
  );
  const s = await r.json().catch(() => ({}));
  if (!r.ok) {
    return json({ error: "stripe_error", message: "We could not look up that order. Try again in a minute." }, 502);
  }
  if (s.payment_status !== "paid") {
    return json({
      error: "not_paid",
      message: "That order is not marked paid yet. If you just paid, wait a minute and refresh. Your Stripe receipt is proof of payment.",
    }, 402);
  }

  const sku = String((s.metadata && s.metadata.sku) || "");
  const email = String(
    s.customer_email || (s.customer_details && s.customer_details.email) || s.client_reference_id || ""
  ).trim().toLowerCase();
  const item = CATALOG.find((p) => p.sku === sku);
  if (!item || item.status !== "live" || !email) {
    return json({ error: "unknown_order", message: "We could not match that order to a product." }, 404);
  }

  const origin = new URL(request.url).origin;
  const skus = item.bundle_of || [item.sku];
  const downloads = [];
  for (const sk of skus) {
    const line = CATALOG.find((p) => p.sku === sk);
    const token = await signDownloadToken(env.DOWNLOAD_SECRET, sk, email, 72);
    downloads.push({
      sku: sk,
      name: line ? line.name : sk,
      url: `${origin}/api/download?token=${token}`,
    });
  }
  return json({ email, downloads });
}
