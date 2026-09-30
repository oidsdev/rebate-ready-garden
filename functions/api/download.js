// GET /api/download?token= — validate the HMAC-signed token and serve the file.
// Tokens expire after 72h. Serves the placeholder PDFs until David's real
// plan PDFs replace them in public/downloads/ (same filenames).
import { CATALOG } from "../_catalog.js";
import { verifyDownloadToken } from "../_shared.js";

export async function onRequestGet({ request, env }) {
  const token = new URL(request.url).searchParams.get("token") || "";
  if (!env.DOWNLOAD_SECRET) {
    return new Response("Downloads are not configured yet.", { status: 503 });
  }
  const v = await verifyDownloadToken(env.DOWNLOAD_SECRET, token);
  if (!v.ok) {
    return new Response(
      v.expired ? "This download link has expired. Email us and we will reissue it."
                : "Invalid download link.",
      { status: v.expired ? 410 : 403 }
    );
  }
  const item = CATALOG.find((p) => p.sku === v.sku);
  if (!item || item.bundle_of) {
    return new Response("Unknown product.", { status: 404 });
  }
  const url = new URL(`/downloads/${v.sku}.pdf`, request.url);
  const file = await fetch(url);
  if (!file.ok) return new Response("File not found.", { status: 404 });
  const headers = new Headers(file.headers);
  headers.set("Content-Type", "application/pdf");
  headers.set("Content-Disposition", `attachment; filename="${v.sku}.pdf"`);
  headers.set("Cache-Control", "private, max-age=0, no-store");
  return new Response(file.body, { headers });
}
