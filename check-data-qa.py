#!/usr/bin/env python3
# check-data-qa.py — data QA for the generated catalog (audit P11).
# Catches blurb-vs-specs drift: plant counts and square footage stated in the
# marketing blurb must match the specs object. Fails loudly on mismatch.
import json, re, sys, pathlib

root = pathlib.Path(__file__).parent
catalog = json.loads((root / "public" / "products.json").read_text())
fails = []
checked = 0

for p in catalog:
    if p.get("status") != "live":
        continue
    sku = p["sku"]
    blurb = p.get("blurb", "")
    specs = p.get("specs", {})

    # 1. plant count: blurb "22 plants" vs specs.plants "22 plants"
    bm = re.search(r"(\d+)\s+plants?", blurb)
    sp = str(specs.get("plants", ""))
    sm = re.search(r"(\d+)", sp)
    if bm and sm:
        checked += 1
        if bm.group(1) != sm.group(1):
            fails.append(f"{sku}: blurb says {bm.group(1)} plants, specs.plants says {sm.group(1)}")

    # 2. dimensions: blurb "20 x 5 ft" product vs sku sqft (pg-rain-100 -> 100)
    dm = re.search(r"(\d+)\s*[x×]\s*(\d+)\s*ft", blurb)
    qm = re.search(r"-(\d+)$", sku)
    if dm and qm:
        checked += 1
        area = int(dm.group(1)) * int(dm.group(2))
        if area != int(qm.group(1)):
            fails.append(f"{sku}: blurb dimensions {dm.group(1)}x{dm.group(2)} = {area} sq ft, sku says {qm.group(1)}")

    # 3. specs.size sqft vs sku sqft
    sm2 = re.search(r"(\d+)\s*sq\s*ft", specs.get("size", ""))
    if sm2 and qm:
        checked += 1
        if sm2.group(1) != qm.group(1):
            fails.append(f"{sku}: specs.size {sm2.group(1)} sq ft, sku says {qm.group(1)}")

if fails:
    print("DATA QA FAILURES:")
    for f in fails:
        print(" -", f)
    sys.exit(1)
print(f"data QA clean ({checked} cross-checks across {len([p for p in catalog if p.get('status')=='live'])} live SKUs)")
