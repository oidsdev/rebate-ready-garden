// POST /api/checkout — create a Stripe Checkout Session (test mode).
// Body: { sku, email }. Returns { url } to redirect the buyer to.
// Requires env.STRIPE_SECRET_KEY; returns a clear 503 when it is unset.
import { CATALOG } from "../_catalog.js";
import { json } from "../_shared.js";

function stripeForm(params) {
  return Object.entries(params)
    .map(([k, v]) => `${encodeURIComponent(k)}=${encodeURIComponent(v)}`)
    .join("&");
}

export async function onRequestPost({ request, env }) {
  const secret = env.STRIPE_SECRET_KEY;
  if (!secret) {
    return json({
      error: "stripe_not_configured",
      message: "Payments are not live yet. Stripe test keys have not been installed on this deployment.",
    }, 503);
  }
  let body;
  try { body = await request.json(); }
  catch { return json({ error: "bad_request", message: "Expected JSON body." }, 400); }

  const sku = String(body.sku || "");
  const email = String(body.email || "").trim().toLowerCase();
  const item = CATALOG.find((p) => p.sku === sku);
  if (!item) return json({ error: "unknown_sku", message: "Unknown product." }, 400);
  if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) {
    return json({ error: "bad_email", message: "Enter a valid email for your download link." }, 400);
  }

  const origin = new URL(request.url).origin;
  const form = stripeForm({
    mode: "payment",
    "line_items[0][price_data][currency]": "usd",
    "line_items[0][price_data][product_data][name]": `${item.name} — Rebate-Ready Garden (Orbital Desk LLC)`,
    "line_items[0][price_data][unit_amount]": String(item.price_cents),
    "line_items[0][quantity]": "1",
    customer_email: email,
    client_reference_id: email,
    "metadata[sku]": sku,
    "metadata[product]": "rebate-ready-garden",
    success_url: `${origin}/success.html?session_id={CHECKOUT_SESSION_ID}`,
    cancel_url: `${origin}/?canceled=1`,
  });

  const r = await fetch("https://api.stripe.com/v1/checkout/sessions", {
    method: "POST",
    headers: {
      Authorization: "Basic " + btoa(secret + ":"),
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: form,
  });
  const data = await r.json().catch(() => ({}));
  if (!r.ok) {
    const se = data.error || {};
    return json({
      error: "stripe_error",
      message: "Stripe refused the checkout request. Try again in a minute.",
      stripe_code: se.code || null,
      stripe_message: typeof se.message === "string" ? se.message.slice(0, 200) : null,
    }, 502);
  }
  return json({ url: data.url });
}
