#!/usr/bin/env python3
"""One-shot generator: catalog (JSON + JS), placeholder PDFs, database page."""
import csv, json, os, html

ROOT = os.path.dirname(os.path.abspath(__file__))
PUB = os.path.join(ROOT, "public")
FN = os.path.join(ROOT, "functions")
os.makedirs(os.path.join(PUB, "downloads"), exist_ok=True)

# ---------- 1. Catalog ----------
# MARKETS is the scalability contract: adding a market = one entry here +
# its plans below + its PDFs in public/downloads/. No new domain, no new
# project, no code changes. status: "live" sells, "coming_soon" shows a
# teaser card with no buy button (checkout also rejects it server-side).
MARKETS = [
    {"id": "maryland", "name": "Maryland", "status": "live",
     "program": "Prince George's Rain Check; Montgomery County RainScapes",
     "editions": [
         {"id": "pg", "label": "Prince George's edition"},
         {"id": "moco", "label": "Montgomery Co. edition"},
         {"id": "bundle", "label": "Bundle"},
     ]},
    {"id": "dc", "name": "District of Columbia", "status": "coming_soon",
     "program": "RiverSmart Homes Rain Garden Rebate (DOEE)",
     "editions": [
         {"id": "dc", "label": "DC edition"},
     ]},
    {"id": "long-island", "name": "Long Island, NY", "status": "coming_soon",
     "program": "Long Island Garden Rewards (NEIWPCC); Town of North Hempstead Native Plant Rebate",
     "editions": [
         {"id": "li", "label": "Long Island edition"},
     ]},
]

PLANS = [
    # (sku, name, edition, market, price_cents, status, blurb)
    ("pg-rain-sun", "Prince George's Rain Garden Plan — Full Sun", "pg", "maryland", 1950, "live",
     "Sized for the Rain Check rain garden rebate. Full-sun plant list."),
    ("pg-rain-shade", "Prince George's Rain Garden Plan — Part Shade", "pg", "maryland", 1950, "live",
     "Sized for the Rain Check rain garden rebate. Part-shade plant list."),
    ("pg-cons-sun", "Prince George's Conservation Landscape — Full Sun", "pg", "maryland", 1950, "live",
     "Sized for the Rain Check conservation landscaping rebate."),
    ("pg-cons-shade", "Prince George's Conservation Landscape — Part Shade", "pg", "maryland", 1950, "live",
     "Sized for the Rain Check conservation landscaping rebate."),
    ("pg-small-lot", "Prince George's Small-Lot Rain Garden", "pg", "maryland", 1950, "live",
     "Compact rain garden for smaller parcels. Rain Check sized."),
    ("mc-rain-sun", "Montgomery County Rain Garden Plan — Full Sun", "moco", "maryland", 1950, "live",
     "Sized for RainScapes rain garden rebates. Full-sun plant list."),
    ("mc-rain-shade", "Montgomery County Rain Garden Plan — Part Shade", "moco", "maryland", 1950, "live",
     "Sized for RainScapes rain garden rebates. Part-shade plant list."),
    ("mc-cons-sun", "Montgomery County Conservation Landscape — Full Sun", "moco", "maryland", 1950, "live",
     "Sized for RainScapes conservation landscape rebates."),
    ("mc-cons-shade", "Montgomery County Conservation Landscape — Part Shade", "moco", "maryland", 1950, "live",
     "Sized for RainScapes conservation landscape rebates."),
    ("mc-small-lot", "Montgomery County Small-Lot Rain Garden", "moco", "maryland", 1950, "live",
     "Compact rain garden for smaller parcels. RainScapes sized."),
    ("dc-rain-50", "DC Rain Garden Plan — 50 sq ft", "dc", "dc", 1950, "coming_soon",
     "Sized for the RiverSmart Homes rebate ($41/sq ft, up to $3,000). Chesapeake-watershed natives only."),
    ("dc-rain-75", "DC Rain Garden Plan — 75 sq ft", "dc", "dc", 1950, "coming_soon",
     "Sized for the RiverSmart Homes rebate ($41/sq ft, up to $3,000). Chesapeake-watershed natives only."),
    ("li-rain-100", "Long Island Rain Garden Plan — 100 sq ft", "li", "long-island", 1200, "coming_soon",
     "Sized for Long Island Garden Rewards (up to $500 in materials). NYFA-listed natives only."),
    ("li-rain-150", "Long Island Rain Garden Plan — 150 sq ft", "li", "long-island", 1200, "coming_soon",
     "Sized for Long Island Garden Rewards (up to $500 in materials). NYFA-listed natives only."),
    ("li-native-100", "Long Island Native Garden Plan — 100 sq ft", "li", "long-island", 1200, "coming_soon",
     "Sized for the North Hempstead native plant rebate (up to $350). NYFA-listed natives only."),
]
catalog = []
for sku, name, edition, market, price_cents, status, blurb in PLANS:
    dollars = price_cents // 100
    catalog.append({
        "sku": sku, "name": name, "edition": edition, "market": market,
        "price_cents": price_cents, "price": f"${dollars}",
        "status": status,
        "blurb": blurb,
        "file": f"/downloads/{sku}.pdf" if status == "live" else None,
        "includes": [
            "To-scale planting layout",
            "Native plant list with sizes, quantities, and spacing",
            "Rebate compliance packet matched to the county program rules",
            "Application submission sheet",
        ],
    })
catalog.append({
    "sku": "md-bundle", "name": "Maryland Bundle — All 10 Plans", "edition": "bundle",
    "market": "maryland",
    "price_cents": 5900, "price": "$59",
    "status": "live",
    "blurb": "Every plan in both county editions. One download, ten packets.",
    "file": None, "bundle_of": [p[0] for p in PLANS if p[5] == "live"],
    "includes": ["All 10 county-edition plans", "All compliance packets and submission sheets"],
})

with open(os.path.join(PUB, "products.json"), "w") as f:
    json.dump(catalog, f, indent=2)
with open(os.path.join(PUB, "markets.json"), "w") as f:
    json.dump(MARKETS, f, indent=2)
with open(os.path.join(FN, "_catalog.js"), "w") as f:
    f.write("// Generated by gen.py — do not hand-edit.\nexport const CATALOG = ")
    f.write(json.dumps(catalog, indent=2))
    f.write(";\n")
print("catalog:", len(catalog), "skus;", len(MARKETS), "markets")

# ---------- 2. Placeholder PDFs ----------
def pdf_bytes(title):
    # Minimal valid single-page PDF with clear placeholder text.
    lines = [
        b"%PDF-1.4",
        b"1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj",
        b"2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj",
        b"3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        b"/Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >> endobj",
        b"4 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj",
    ]
    content = (
        b"BT /F1 20 Tf 72 720 Td (PLACEHOLDER PDF) Tj ET\n"
        b"BT /F1 12 Tf 72 690 Td (" + title.encode("latin-1", "replace")[:60] + b") Tj ET\n"
        b"BT /F1 12 Tf 72 660 Td (This is a placeholder. The real compliance packet) Tj ET\n"
        b"BT /F1 12 Tf 72 644 Td (and planting plan PDF will replace this file.) Tj ET\n"
    )
    lines.append(b"5 0 obj << /Length %d >> stream" % len(content))
    lines.append(content + b"endstream endobj")
    body = b"\n".join(lines) + b"\n"
    # xref
    offsets = []
    pos = 0
    parts = body.split(b"\n")
    # rebuild with offsets: simpler — track object starts
    out = b"%PDF-1.4\n"
    objs = [
        b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n",
        b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n",
        b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        b"/Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>\nendobj\n",
        b"4 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n",
        b"5 0 obj\n<< /Length %d >>\nstream\n" % len(content) + content + b"endstream\nendobj\n",
    ]
    offs = []
    for o in objs:
        offs.append(len(out))
        out += o
    xref_pos = len(out)
    out += b"xref\n0 6\n0000000000 65535 f \n"
    for o in offs:
        out += b"%010d 00000 n \n" % o
    out += (b"trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n" % xref_pos)
    return out

for item in catalog:
    if item.get("status") != "live":
        continue  # coming_soon: no placeholder, nothing to sell yet
    skus = item.get("bundle_of") or [item["sku"]]
    for sku in skus:
        p = os.path.join(PUB, "downloads", f"{sku}.pdf")
        if not os.path.exists(p):
            with open(p, "wb") as f:
                f.write(pdf_bytes(item["name"] if sku == item["sku"] else sku))
print("pdfs done")

# ---------- 3. Database page from CSV ----------
rows = []
with open(os.path.join(ROOT, "rebate-database.csv"), newline="") as f:
    r = csv.DictReader(f)
    for row in r:
        rows.append(row)

def esc(s): return html.escape(s or "")

cards = []
for row in rows:
    cards.append(f"""<article class="db-card">
<h3>{esc(row['Program'])}</h3>
<dl>
<dt>Rebate</dt><dd>{esc(row['Rebate'])}</dd>
<dt>Cap</dt><dd>{esc(row['Cap'])}</dd>
<dt>Plan required</dt><dd>{esc(row['Plan required'])}</dd>
<dt>DIY allowed</dt><dd>{esc(row['DIY OK'])}</dd>
<dt>Status (checked 9/30/26)</dt><dd>{esc(row['Open (9/30/26)'])}</dd>
</dl>
<p class="src"><a href="{esc(row['Source'])}" rel="noopener">Official source</a></p>
</article>""")

page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Free Database: 23 Stormwater Rebate Programs (MD, DC, VA, DE, PA, NJ, NY, New England) | Rebate-Ready Garden</title>
<meta name="description" content="A free, checked directory of 23 residential stormwater and native-plant rebate programs across Maryland, DC, Virginia, Delaware, Pennsylvania, New Jersey, New York, and New England. Rebate rates, caps, and official sources.">
<meta property="og:title" content="Free: 23 Stormwater Rebate Programs, Checked 9/30/26">
<meta property="og:description" content="Rebate rates, caps, and official sources for residential stormwater programs across the Mid-Atlantic and Northeast.">
<meta property="og:type" content="website">
<link rel="stylesheet" href="/style.css">
</head>
<body>
<header class="site"><div class="wrap">
<a class="brand" href="/">Rebate-Ready Garden</a>
<nav><a href="/prince-georges.html">Prince George's</a><a href="/montgomery-county.html">Montgomery Co.</a><a href="/rockville-gaithersburg.html">Rockville/Gaithersburg</a><a href="/rebate-database.html">Free Database</a><a href="/faq.html">FAQ</a></nav>
</div></header>
<main class="wrap">
<h1>23 stormwater rebate programs, checked September 30, 2026</h1>
<p class="lede">Every residential program we could verify across Maryland, DC, Virginia, Delaware, Pennsylvania, New Jersey, New York, and New England. Free to use. Programs change their rules, so confirm with the official source before you apply.</p>
<p class="note">Programs marked UNVERIFIED in our working sheet are not listed here. What is listed was confirmed open or confirmed real as of the check date.</p>
<div class="db-grid">
{''.join(cards)}
</div>
<section class="cta">
<h2>Applying to a Maryland program?</h2>
<p>Our compliance-ready planting plans include the layout, the native plant list, and the application packet your county asks for. $19.50 per plan.</p>
<p><a class="btn" href="/">See the plans</a></p>
</section>
</main>
<footer class="site"><div class="wrap">
<p>(c) Orbital Desk LLC &middot; Published by Orbital Desk LLC</p>
</div></footer>
</body>
</html>"""
with open(os.path.join(PUB, "rebate-database.html"), "w") as f:
    f.write(page)
print("database page:", len(rows), "programs")
