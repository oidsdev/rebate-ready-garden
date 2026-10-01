#!/usr/bin/env python3
"""Catalog generator for Rebate-Ready Garden.

REBUILT 2026-10-01 to match the live production catalog EXACTLY (field for
field, including the specs objects and their quirks). The previous version
described a stale catalog and would have REGRESSED production if run.

Rule: this file is the single source of truth for products.json /
markets.json / functions/_catalog.js. After ANY production catalog change,
update the tables below first, then run this script, then diff against
production before deploying.

What it does:
  1. Writes public/products.json, public/markets.json, functions/_catalog.js
  2. Creates placeholder PDFs ONLY for live SKUs whose PDF is missing
     (never overwrites an existing PDF).

What it does NOT do:
  - It does NOT generate public/rebate-database.html. That page is
    hand-maintained (state headings, jump links, verified cards). Do not
    add database generation back here without also replicating the
    hand-built structure.
  - It does NOT touch any other HTML page.

Adding a new location = add its market entry (if new state), its PLANS
rows (with specs), build its real PDFs into public/downloads/, run this
script, verify byte-identical catalog output for unchanged SKUs, deploy.
"""
import json, os

ROOT = os.path.dirname(os.path.abspath(__file__))
PUB = os.path.join(ROOT, "public")
FN = os.path.join(ROOT, "functions")
os.makedirs(os.path.join(PUB, "downloads"), exist_ok=True)

INCLUDES = [
    "To-scale planting layout",
    "Native plant list with sizes, quantities, and spacing",
    "Rebate compliance packet matched to the program rules",
    "Application submission sheet",
    "Install it yourself over a weekend, or hand the packet to any landscaper for a bid",
]

# ---------- 1. Catalog ----------
# status: "live" sells, "coming_soon" shows a teaser card with no buy
# button (checkout also rejects it server-side).
MARKETS = [
    {"id": "maryland", "name": "Maryland", "status": "live",
     "program": "Prince George's County Rain Check Rebate; Montgomery County RainScapes Rewards",
     "editions": [
         {"id": "pg", "label": "Prince George's edition"},
         {"id": "bundle", "label": "Bundle"},
         {"id": "moco", "label": "Montgomery Co. edition"},
     ]},
    {"id": "dc", "name": "District of Columbia", "status": "live",
     "program": "RiverSmart Homes Rain Garden Rebate (DOEE)",
     "editions": [
         {"id": "dc", "label": "DC edition"},
     ]},
]

# (sku, name, edition, market, price_cents, status, blurb, specs)
# specs transcribed verbatim from production 2026-10-01 (quirks included:
# some plants values are ints, some strings; blurb plant counts and specs
# plant counts differ on a few SKUs — that is production truth, not a typo
# to "fix" here).
PLANS = [
    ("pg-rain-100", "Prince George's Rain Garden Plan \u2014 100 sq ft", "pg", "maryland", 1950, "live",
     "20 \u00d7 5 ft rain garden, 22 plants, full sun to part shade. Sized for the Rain Check rebate ($10/sq ft).",
     {"size": "20 \u00d7 5 ft \u00b7 100 sq ft", "plants": "22 plants", "sun": "Full sun to part shade",
      "rebate": "Up to $1,000", "rebate_note": "$10/sq ft rain garden rate"}),
    ("pg-rain-150", "Prince George's Rain Garden Plan \u2014 150 sq ft", "pg", "maryland", 1950, "live",
     "25 \u00d7 6 ft rain garden, 30 plants, full sun to part shade. Sized for the Rain Check rebate ($10/sq ft).",
     {"size": "25 \u00d7 6 ft \u00b7 150 sq ft", "plants": "30 plants", "sun": "Full sun to part shade",
      "rebate": "Up to $1,500", "rebate_note": "$10/sq ft rain garden rate"}),
    ("pg-rain-200", "Prince George's Rain Garden Plan \u2014 200 sq ft", "pg", "maryland", 1950, "live",
     "25 \u00d7 8 ft rain garden, 42 plants, full sun to part shade. Sized for the Rain Check rebate ($10/sq ft).",
     {"size": "25 \u00d7 8 ft \u00b7 200 sq ft", "plants": "42 plants", "sun": "Full sun to part shade",
      "rebate": "Up to $2,000", "rebate_note": "$10/sq ft rain garden rate"}),
    ("pg-meadow-250", "Prince George's Lawn-to-Meadow Plan \u2014 250 sq ft", "pg", "maryland", 1950, "live",
     "25 \u00d7 10 ft lawn-to-meadow, 55 plants, full sun. Sized for the Rain Check conservation rebate ($5/sq ft).",
     {"size": "25 \u00d7 10 ft \u00b7 250 sq ft", "plants": 60, "sun": "Full sun",
      "rebate": "Up to $1,250", "rebate_note": "$5/sq ft conservation landscaping rate"}),
    ("pg-meadow-400", "Prince George's Lawn-to-Meadow Plan \u2014 400 sq ft", "pg", "maryland", 1950, "live",
     "40 \u00d7 10 ft lawn-to-meadow, 85 plants, full sun. Sized for the Rain Check conservation rebate ($5/sq ft).",
     {"size": "40 \u00d7 10 ft \u00b7 400 sq ft", "plants": 89, "sun": "Full sun",
      "rebate": "Up to $2,000", "rebate_note": "$5/sq ft conservation landscaping rate"}),
    ("dc-rain-50", "DC Rain Garden Plan \u2014 50 sq ft", "dc", "dc", 1950, "live",
     "10 \u00d7 5 ft rain garden, 18 plants, full sun to part shade. Sized for the RiverSmart Homes rebate ($41/sq ft, up to $3,000). Chesapeake-watershed natives only.",
     {"size": "10 \u00d7 5 ft \u00b7 50 sq ft", "plants": "18 plants", "sun": "Full sun to part shade",
      "rebate": "Up to $2,050", "rebate_note": "$41/sq ft RiverSmart rate"}),
    ("dc-rain-75", "DC Rain Garden Plan \u2014 75 sq ft", "dc", "dc", 1950, "live",
     "15 \u00d7 5 ft rain garden, 27 plants, full sun to part shade. Sized for the RiverSmart Homes rebate ($41/sq ft, up to $3,000). Chesapeake-watershed natives only.",
     {"size": "15 \u00d7 5 ft \u00b7 75 sq ft", "plants": "27 plants", "sun": "Full sun to part shade",
      "rebate": "Up to $3,000", "rebate_note": "$41/sq ft rate, program cap"}),
    ("mc-rain-100", "Montgomery County Rain Garden Plan \u2014 100 sq ft", "moco", "maryland", 1950, "live",
     "20 \u00d7 5 ft rain garden, 35 plants, full sun to part shade. Sized for RainScapes ($10/sq ft).",
     {"size": "20 \u00d7 5 ft \u00b7 100 sq ft", "plants": 40, "sun": "Full sun to part shade",
      "rebate": "Up to $1,000", "rebate_note": "$10/sq ft rain garden rate"}),
    ("mc-rain-150", "Montgomery County Rain Garden Plan \u2014 150 sq ft", "moco", "maryland", 1950, "live",
     "25 \u00d7 6 ft rain garden, 50 plants, full sun to part shade. Sized for RainScapes ($10/sq ft).",
     {"size": "25 \u00d7 6 ft \u00b7 150 sq ft", "plants": 55, "sun": "Full sun to part shade",
      "rebate": "Up to $1,500", "rebate_note": "$10/sq ft rain garden rate"}),
    ("mc-rain-200", "Montgomery County Rain Garden Plan \u2014 200 sq ft", "moco", "maryland", 1950, "live",
     "25 \u00d7 8 ft rain garden, 71 plants, full sun to part shade. Sized for RainScapes ($10/sq ft).",
     {"size": "25 \u00d7 8 ft \u00b7 200 sq ft", "plants": 72, "sun": "Full sun to part shade",
      "rebate": "Up to $2,000", "rebate_note": "$10/sq ft rain garden rate"}),
    ("mc-meadow-250", "Montgomery County Lawn-to-Meadow Plan \u2014 250 sq ft", "moco", "maryland", 1950, "live",
     "25 \u00d7 10 ft meadow conversion, 93 plants, full sun. Sized for RainScapes conservation landscaping ($5\u2013$6/sq ft).",
     {"size": "25 \u00d7 10 ft \u00b7 250 sq ft", "plants": 96, "sun": "Full sun",
      "rebate": "Up to $1,500", "rebate_note": "$5\u2013$6/sq ft conservation landscaping rate"}),
    ("mc-meadow-400", "Montgomery County Lawn-to-Meadow Plan \u2014 400 sq ft", "moco", "maryland", 1950, "live",
     "40 \u00d7 10 ft meadow conversion, 146 plants, full sun. Sized for RainScapes conservation landscaping ($5\u2013$6/sq ft).",
     {"size": "40 \u00d7 10 ft \u00b7 400 sq ft", "plants": "146 plants", "sun": "Full sun",
      "rebate": "Up to $2,400", "rebate_note": "$5\u2013$6/sq ft conservation landscaping rate"}),
]

catalog = []
for sku, name, edition, market, price_cents, status, blurb, specs in PLANS:
    dollars = price_cents // 100
    cents = price_cents % 100
    catalog.append({
        "sku": sku, "name": name, "edition": edition, "market": market,
        "price_cents": price_cents, "price": f"${dollars}.{cents:02d}",
        "status": status,
        "blurb": blurb,
        "file": f"/downloads/{sku}.pdf" if status == "live" else None,
        "includes": list(INCLUDES),
        "specs": dict(specs),
    })
catalog.append({
    "sku": "pg-bundle", "name": "Prince George's Bundle \u2014 All 5 Plans",
    "edition": "bundle", "market": "maryland",
    "price_cents": 2450, "price": "$24.50",
    "status": "live",
    "blurb": "Every Prince George's plan: three rain gardens and two lawn-to-meadow conversions. Five packets, one download.",
    "file": None,
    "bundle_of": ["pg-rain-100", "pg-rain-150", "pg-rain-200", "pg-meadow-250", "pg-meadow-400"],
    "includes": ["All 5 Prince George's plans", "All compliance packets and submission sheets"],
})

with open(os.path.join(PUB, "products.json"), "w") as f:
    json.dump(catalog, f, indent=2)
with open(os.path.join(PUB, "markets.json"), "w") as f:
    json.dump(MARKETS, f, indent=2)
with open(os.path.join(FN, "_catalog.js"), "w") as f:
    f.write("// Generated by gen.py \u2014 do not hand-edit.\nexport const CATALOG = ")
    f.write(json.dumps(catalog, indent=2))
    f.write(";\n")
print("catalog:", len(catalog), "skus;", len(MARKETS), "markets")

# ---------- 2. Placeholder PDFs (missing live PDFs only, never overwrite) ----------
def pdf_bytes(title):
    content = (
        b"BT /F1 20 Tf 72 720 Td (PLACEHOLDER PDF) Tj ET\n"
        b"BT /F1 12 Tf 72 690 Td (" + title.encode("latin-1", "replace")[:60] + b") Tj ET\n"
        b"BT /F1 12 Tf 72 660 Td (This is a placeholder. The real compliance packet) Tj ET\n"
        b"BT /F1 12 Tf 72 644 Td (and planting plan PDF will replace this file.) Tj ET\n"
    )
    objs = [
        b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n",
        b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n",
        b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        b"/Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>\nendobj\n",
        b"4 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n",
        b"5 0 obj\n<< /Length %d >>\nstream\n" % len(content) + content + b"endstream\nendobj\n",
    ]
    out = b"%PDF-1.4\n"
    offs = []
    for o in objs:
        offs.append(len(out))
        out += o
    xref_pos = len(out)
    out += b"xref\n0 6\n0000000000 65535 f \n"
    for o in offs:
        out += b"%010d 00000 n \n" % o
    out += b"trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n" % xref_pos
    return out

made = 0
for item in catalog:
    if item.get("status") != "live":
        continue  # coming_soon: no placeholder, nothing to sell yet
    skus = item.get("bundle_of") or [item["sku"]]
    for sku in skus:
        p = os.path.join(PUB, "downloads", f"{sku}.pdf")
        if not os.path.exists(p):
            with open(p, "wb") as f:
                f.write(pdf_bytes(item["name"] if sku == item["sku"] else sku))
            made += 1
print("placeholders created:", made, "(existing PDFs untouched)")

# ---------- 3. Database page ----------
# INTENTIONALLY ABSENT. public/rebate-database.html is hand-maintained
# (state headings, jump links, verified card content). Do not regenerate
# it from the CSV here; the CSV still contains raw booleans, truncated
# source cells, and stale research wording that must not reach production.
print("database page: hand-maintained, skipped")
