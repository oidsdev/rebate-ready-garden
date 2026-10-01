# Compliance QA — 15 final Rebate-Ready Garden plan PDFs
**Date:** 2026-10-01 · **Reviewer:** Muse (non-professional issue-spotting — NOT legal advice)
**Source files:** `~/workspace/rebate-garden/pdf-staging/*.pdf` (15 files, 5 pages each, text extracted via pdftotext)
**Reference:** `~/workspace/rebate-garden/legal-review-decisions.md` (2026-09-30) + `rebate-database.csv`

## Method
- Full text extraction of all 15 PDFs; greps for banned phrases ("designed", "landscape plan", "landscape architect", "expert", "professionally designed"), guarantee language, refund/terms references, 811 / perc-test / confirm-rules, plan numbers, edition headers, "rules checked" dates, source lines, placeholder artifacts (lorem/TODO/XXX/[insert]/"coming soon").
- Rate/rule cross-check against `rebate-database.csv`.
- Rendered page-1 illustration of one PDF to confirm no government logos/marks (all 15 PDFs embed exactly 2 JPEG illustrations each: the to-scale planting layout and the plant-height figure — hand-drawn style, no program logos).

## Verdicts (all 15)

| PDF | Plan No. | Verdict | Notes |
|---|---|---|---|
| MD-PG-RainGarden-100sqft.pdf | MD-01 | **PASS** (minor notes) | See shared notes A, F |
| MD-PG-RainGarden-150sqft.pdf | MD-02 | **PASS** (minor notes) | A, F |
| MD-PG-RainGarden-200sqft.pdf | MD-03 | **PASS** (minor notes) | A, F |
| MD-PG-LawnToMeadow-250sqft.pdf | MD-04 | **PASS** (minor notes) | A, F, G |
| MD-PG-LawnToMeadow-400sqft.pdf | MD-05 | **PASS** (minor notes) | A, F, G |
| MD-MC-RainGarden-100sqft.pdf | MD-06 | **FLAG** | B (stale-rate risk), C (typo), A, F |
| MD-MC-RainGarden-150sqft.pdf | MD-07 | **FLAG** | B, C, A, F |
| MD-MC-RainGarden-200sqft.pdf | MD-08 | **FLAG** | B, C, A, F |
| MD-MC-LawnToMeadow-250sqft.pdf | MD-09 | **FLAG** | B, C, A, F |
| MD-MC-LawnToMeadow-400sqft.pdf | MD-10 | **FLAG** | B, C, A, F |
| DC-RainGarden-50sqft.pdf | DC-11 | **PASS** (minor notes) | D, A, F |
| DC-RainGarden-75sqft.pdf | DC-12 | **PASS** (minor notes) | D, A, F |
| LI-RainGarden-100sqft.pdf | LI-13 | **FLAG** | E (TONH deadline), A, F |
| LI-RainGarden-150sqft.pdf | LI-14 | **FLAG** | E, A, F |
| LI-LawnToMeadow-100sqft.pdf | LI-15 | **FLAG** | E, A, F |

**Shared notes:**
- **A (all 15): No 14-day refund policy or Terms-of-Sale reference anywhere in the PDFs.** Zero hits for "refund", "14-day", "terms of sale" across all 15 files. The decided position (memo #3) puts the policy pre-checkout on the storefront, which is satisfied — but a buyer who only ever sees the PDF has no refund information. Recommended fix: one line on page 5, e.g. "14-day refund policy — see Terms of Sale at rebatereadygarden.com/terms.html." Not a ship-blocker per the memo, but a gap worth closing.
- **F (all 15): Dated-edition footer is partial.** Each PDF carries "© 2026 Orbital Desk LLC · The Rebate-Ready Garden · [Edition] Edition" (year only) plus "rules checked Sept 30, 2026" on page 4. The memo's gate was "edition date + program-rules version" — the rules version is there; the edition date is year-granularity only. Consider "Edition of September 30, 2026" in the footer. Minor.
- **B (MD-MC ×5): Montgomery County rates are from the county's 2018 table — flagged IN the PDF's own sources line.** Page 5 sources: "…montgomerycountymd.gov/propertycare/rainscapes (checked 9/30/26). County per-sq-ft rates are from its 2018 table; confirm current rates with your planner.." Two problems: (1) the rates ($10 rain garden / $5 lawn-to-meadow) may be stale — we emailed RainScapes@montgomerycountymd.gov on 2026-09-30 and have no reply yet; (2) literal typo — double period after "planner.." in all 5 MD-MC PDFs (note C). The in-PDF "confirm with your planner" instruction mitigates the legal risk, but **these 5 should not ship until the county confirms current rates or we re-source them.**
- **D (DC ×2): rate follows the live DOEE page ($41/sq ft, $3,000 cap — source cited, checked 9/30/26).** The database records a conflict: the Alliance's 2020–2021 homeowner guide says $2,200 max. The PDF does not acknowledge the older conflicting figure. Sourced and current as presented; no violation — but if the Alliance figure is what buyers encounter, expect confusion. Watch item, not a blocker.
- **E (LI ×3): Town of North Hempstead program deadline is Oct 1, 2026 (today) per the database — the PDFs never mention it.** The packet covers Garden Rewards ($500 cap, "fall round: by Oct 31 or until funds run out" — good) and North Hempstead ($350 cap), and names the Peconic Estuary program in step-by-step ("Check which program you're in: Garden Rewards, North Hempstead, or Peconic Estuary") without any Peconic-specific rates/steps. North Hempstead buyers reading this after Oct 1 could apply to a closed program. **Fix: add the TONH deadline (or a "check current status" line) before shipping the LI editions.** Peconic detail is a minor gap.
- **G (MD-PG lawn-to-meadow ×2): database notes "Track 3 min 1,000 sq ft" for PG conservation landscaping (DB entry truncated, full rule unverified).** The PDF states minimum 250 sq ft with no mention of Track 3. Cannot verify from available sources — flag for the county-compliance pass, not a confirmed error.

## What passed cleanly in all 15
1. **No expert/professional-design claims.** Zero hits for "designed", "landscape plan", "landscape architect", "expert-designed", "professionally designed". Framing used: "Independent guide", "printable plan". ("Design sketch" appears only as the name of paperwork the program itself requires.)
2. **No rebate guarantees.** Every "WHAT THE PROGRAM PAYS" headline reads "at most $X, if approved" (per the ad-claims pass), each packet repeats "Approval isn't guaranteed" plus "the rebate can never be more than what you actually spend, with itemized receipts; labor you do yourself doesn't count", and closes with "Approval isn't guaranteed; the program's current rules always win." Non-endorsement lines name the correct program operators per edition.
3. **Buyer checklist present in all 15:** confirm-current-rules ("confirm with the program before you buy" / "the program's current rules always win"), perc-test steps (full worksheet in rain-garden editions; referenced in lawn-to-meadow), and call-811 (Miss Utility (811)) with "at least 3 business days before digging" in the step-by-step. All 15 also say "Don't buy or dig before written approval" in some form.
4. **No government logos or program marks.** Rendered illustrations are original hand-drawn-style planting layouts; no county/CBT/DOEE/NEIWPCC marks.
5. **Edition/plan consistency.** Unique plan numbers MD-01…MD-10, DC-11/12, LI-13/14/15, matching edition headers in all files; all "rules checked Sept 30, 2026"; all 5 pages; all end with "Not legal advice." and a SOURCES line.
6. **No placeholder artifacts.** No lorem/TODO/XXX/[insert]/"coming soon" text in any file. The "SUPERSEDED (placeholder bug)" issue from last night's Drive copies does not exist in these 15 finals.
7. **Rate math checks out:** DC 50×$41=$2,050 ✓ / 75×$41=$3,075 capped at program max $3,000 ✓; PG/MC rain garden $10/sq ft and lawn-to-meadow $5/sq ft match the database; LI "$500 Garden Rewards / $350 North Hempstead" matches the database (LI lawn-to-meadow also $500 — consistent with Garden Rewards plant/material reimbursement).

## Must-fix before replacing storefront placeholders
1. **MD-MC ×5: resolve the 2018-table rate staleness** — either the county replies to the 9/30 rates email or the rates are re-sourced; fix the "planner.." double-period typo at the same time. (The in-PDF "confirm with your planner" line is good mitigation but not a substitute for current numbers.)
2. **LI ×3: add the North Hempstead program deadline** (Oct 1, 2026 per database — verify whether it is still open before stating it) and either detail or drop the Peconic Estuary reference.
3. **All 15: add the 14-day refund policy + Terms of Sale reference** (one line on the submission-sheet page). Decided storefront position is satisfied; this closes the loop for buyers who never return to the site.
4. Optional: full edition date in the footer ("Edition of September 30, 2026") instead of year-only ©.

## Bottom line
The 15 finals are in strong shape — no banned claims, no guarantees, checklists and non-endorsement language everywhere, no placeholders, editions consistent. Nothing here contradicts the legal-review decisions. The blockers are narrow: Montgomery County rate freshness (5 PDFs), the LI/North Hempstead deadline (3 PDFs), and the missing refund/terms line (all 15). Botanical QA (Grok) is still the other half of dual approval and was not in scope for this pass.
