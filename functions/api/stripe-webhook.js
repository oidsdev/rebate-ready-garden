// POST /api/stripe-webhook — Stripe event receiver.
// Verifies the Stripe-Signature header (HMAC-SHA256, see _shared.js).
// On checkout.session.completed: issues HMAC-signed 72h download tokens.
// Idempotency: in-memory Set of processed event IDs (per-isolate, best
// effort). Before production traffic, back this with KV or D1 so retried
// deliveries can never double-issue links across isolates.
import { CATALOG } from "../_catalog.js";
import { verifyStripeSignature, signDownloadToken, json } from "../_shared.js";

const seen = new Set();
const MAX_SEEN = 5000;

export async function onRequestPost({ request, env }) {
  const v = await verifyStripeSignature(request, env.STRIPE_WEBHOOK_SECRET);
  if (!v.ok) return json({ error: v.error }, v.status);
  const event = v.event;
  const type = event.type || "";
  const obj = (event.data && event.data.object) || {};

  const eventId = String(event.id || "");
  if (eventId) {
    if (seen.has(eventId)) return json({ received: true, duplicate: true });
    seen.add(eventId);
    if (seen.size > MAX_SEEN) {
      const first = seen.values().next().value;
      seen.delete(first);
    }
  }

  if (type === "checkout.session.completed") {
    const sku = String((obj.metadata && obj.metadata.sku) || "");
    const email = String(
      obj.customer_email || obj.customer_details?.email || obj.client_reference_id || ""
    ).trim().toLowerCase();
    const item = CATALOG.find((p) => p.sku === sku);
    if (!item || !email) {
      console.log(`webhook: checkout.session.completed ignored (sku=${sku} email=${email ? "set" : "missing"})`);
      return json({ received: true });
    }
    if (!env.DOWNLOAD_SECRET) {
      return json({ error: "download_misconfigured" }, 500);
    }
    const skus = item.bundle_of || [item.sku];
    const origin = new URL(request.url).origin;
    const downloads = [];
    for (const s of skus) {
      const token = await signDownloadToken(env.DOWNLOAD_SECRET, s, email, 72);
      downloads.push({ sku: s, url: `${origin}/api/download?token=${token}` });
    }
    // TODO: email the download links to the buyer (Resend / Loops / etc.).
    // For now the links are returned in the webhook response for operator use.
    console.log(`webhook: issued ${downloads.length} download link(s) for ${email} (sku=${sku})`);
    return json({ received: true, email, downloads });
  }

  return json({ received: true, ignored: type });
}
