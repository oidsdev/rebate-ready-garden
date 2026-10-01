#!/usr/bin/env python3
# check-prices.py — catch storefront/checkout price mismatches (the 2026-10-01 bug class:
# index.html said $19.50 while functions/_catalog.js charged $39).
# Fails loudly if the distinct advertised prices on public pages don't match
# the distinct charge prices in the checkout catalog.
import re, sys, pathlib, json

root = pathlib.Path(__file__).parent
fails = []

# 1. Charge prices from the checkout catalog (source of truth for money movement)
catalog = (root / "functions" / "_catalog.js").read_text()
charged = set()
for m in re.finditer(r'"price_cents":\s*(\d+)', catalog):
    charged.add(int(m.group(1)) / 100)
print(f"catalog charges: {sorted(charged)}")

# 2. Advertised prices on public pages (exclude rebate amounts, which aren't our prices)
#    Heuristic: prices within ~40 chars of buy/plan/price/checkout/bundle words.
advertised = set()
for html in (root / "public").glob("*.html"):
    text = html.read_text()
    for m in re.finditer(r'\$(\d+\.\d{2})', text):
        ctx = text[max(0, m.start()-40):m.end()+10].lower()
        if re.search(r'buy|plan|price|checkout|bundle|each|only|just', ctx):
            # skip rebate-program amounts (e.g. "$10/sq ft", "Up to $1,000")
            if re.search(r'/sq|rebate|program|pays?', ctx):
                continue
            advertised.add(float(m.group(1)))
print(f"pages advertise: {sorted(advertised)}")

missing = advertised - charged   # advertised but not charged -> customers undercharged or stale copy
extra = charged - advertised     # charged but never advertised -> surprise at checkout
if missing:
    fails.append(f"advertised on pages but NOT in checkout catalog: {sorted(missing)}")
if extra:
    fails.append(f"charged by catalog but NOT advertised on pages: {sorted(extra)}")

# 3. products.json (storefront data) must agree with the catalog
prod = json.loads((root / "public" / "products.json").read_text())
prods = set()
items = prod if isinstance(prod, list) else prod.get("products", prod)
for p in (items if isinstance(items, list) else items.values()):
    if isinstance(p, dict) and p.get("status") == "live" and "price_cents" in p:
        prods.add(p["price_cents"] / 100)
if set(prods) != set(charged):
    fails.append(f"products.json {sorted(prods)} != _catalog.js {sorted(charged)}")

if fails:
    print("PRICE MISMATCH:")
    for f in fails:
        print(" -", f)
    sys.exit(1)
print("prices consistent across pages, products.json, and checkout catalog")
