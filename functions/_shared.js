// Shared helpers for the Rebate-Ready Garden Pages Functions.
// Signature verification mirrors the proven Oids worker implementation
// (~/workspace/oids/worker/index.js, handleStripeWebhook): HMAC-SHA256 of
// "<t>.<payload>" with the webhook secret, 5-minute replay window,
// constant-time hex comparison.

export function hmacEqualHex(a, b) {
  if (a.length !== b.length) return false;
  let diff = 0;
  for (let i = 0; i < a.length; i++) diff |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return diff === 0;
}

export async function hmacHex(secret, message) {
  const key = await crypto.subtle.importKey(
    "raw", new TextEncoder().encode(secret),
    { name: "HMAC", hash: "SHA-256" }, false, ["sign"]
  );
  const mac = await crypto.subtle.sign("HMAC", key, new TextEncoder().encode(message));
  return [...new Uint8Array(mac)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

// Returns { ok: true, event } or { ok: false, status, error }.
export async function verifyStripeSignature(request, secret) {
  if (!secret) return { ok: false, status: 500, error: "webhook_misconfigured" };
  const sig = request.headers.get("stripe-signature") || "";
  const tMatch = sig.match(/t=(\d+)/);
  const v1Match = sig.match(/v1=([a-f0-9]+)/i);
  if (!tMatch || !v1Match) return { ok: false, status: 400, error: "bad_signature" };
  const payload = await request.text();
  if (Math.abs(Date.now() / 1000 - Number(tMatch[1])) > 300) {
    return { ok: false, status: 400, error: "stale_signature" };
  }
  const expected = await hmacHex(secret, `${tMatch[1]}.${payload}`);
  if (!hmacEqualHex(expected, v1Match[1].toLowerCase())) {
    return { ok: false, status: 400, error: "bad_signature" };
  }
  let event;
  try { event = JSON.parse(payload); }
  catch { return { ok: false, status: 400, error: "bad_event" }; }
  return { ok: true, event };
}

// Download tokens: b64url("<sku>.<exp>.<email>") + "." + hex(HMAC(secret, payload))
export function b64urlEncode(s) {
  return btoa(s).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}
export function b64urlDecode(s) {
  s = s.replace(/-/g, "+").replace(/_/g, "/");
  while (s.length % 4) s += "=";
  return atob(s);
}

export async function signDownloadToken(secret, sku, email, ttlHours = 72) {
  const exp = Math.floor(Date.now() / 1000) + ttlHours * 3600;
  const payload = `${sku}.${exp}.${email}`;
  const sig = await hmacHex(secret, payload);
  return `${b64urlEncode(payload)}.${sig}`;
}

export async function verifyDownloadToken(secret, token) {
  const parts = String(token || "").split(".");
  if (parts.length !== 2) return { ok: false };
  let payload;
  try { payload = b64urlDecode(parts[0]); } catch { return { ok: false }; }
  const expected = await hmacHex(secret, payload);
  if (!hmacEqualHex(expected, parts[1].toLowerCase())) return { ok: false };
  const [sku, exp, ...emailParts] = payload.split(".");
  const email = emailParts.join(".");
  if (!sku || !exp || !email) return { ok: false };
  if (Number(exp) * 1000 < Date.now()) return { ok: false, expired: true };
  return { ok: true, sku, email, exp: Number(exp) };
}

export function json(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status, headers: { "Content-Type": "application/json" },
  });
}
