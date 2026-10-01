# Rebate-Ready Garden — Legal Review Decisions
**Orbital Desk LLC · September 30, 2026**
**Prepared by: Muse (non-professional issue-spotting pass — NOT legal advice)**
**Backbone: Claude's lawyer-ready brief (desk-team msgs 207–211, 2026-09-30), team-wide review ordered by David (msg 201)**

> This document records dispositions on every item in the team's legal review: what was decided, what was implemented on the storefront, and what is queued for counsel. It is non-professional issue-spotting feeding David's lawyer, who has the final word. Nothing here is legal advice.

## Standing business facts (affecting the analysis)
- Seller is **Orbital Desk LLC, a New York LLC** (not Maryland-based — corrects the nexus assumption in the brief's §4).
- Product: digital PDF downloads ($39/plan, $59/bundle), sold on our own Stripe storefront. No Etsy/Gumroad at launch.
- Launch volumes are small (scenarios of 5–40 sales/month); remote-seller thresholds are ~$100k or 200 transactions per state.
- Only dual-approved PDFs ship (Grok: botanical; Muse: county compliance). Placeholders never sell.

## Dispositions

### #1 LICENSING — R/Y → mitigations implemented, question to counsel stands
- **Call:** Sell as **reference layouts**, never "designed" or "landscape plan." Verified the whole storefront: neither phrase appears anywhere. Added Terms §2 ("reference layouts, not professional design services; not prepared by a licensed landscape architect; buyer adapts and submits as their own") and a public FAQ answer ("Are these professional landscape designs?").
- **Q-COUNSEL (unchanged):** Does selling adaptable planting templates that buyers submit as their own constitute the "practice" of landscape architecture in MD, PA, DC, or VA? Would pairing with a licensed nursery or LA resolve it?

### #2 LIABILITY — R → terms implemented, insurance question open
- **Call:** Terms of Sale now carry: no guarantee of rebate approval (§3), liability capped at the purchase price with no consequential damages (§5), buyer-responsibility checklist — confirm current program rules, perc test for rain gardens, call 811 before digging (§2). Homepage and FAQ already disclaim approval guarantees; that language stays.
- **Implemented gate:** every shipping PDF must carry the edition date + program-rules version (goes into the dual-approval QA checklist — PDFs are not yet in hand).
- **Q-COUNSEL:** Is a price-cap enforceable against MD consumers? Do we need general liability or E&O insurance?
- **Q-DAVID:** Do you want E&O/general-liability coverage before go-live, or launch without and revisit at revenue?

### #3 CONSUMER PROTECTION / REFUNDS — Y → policy kept, now visible pre-checkout
- **Call:** Kept the published policy (14-day refund if the plan hasn't been submitted with a rebate application) — it is now mirrored word-for-word in Terms §4, linked from every buy button ("Refund policy · Terms of Sale" under each Buy card), in every page footer, and in the FAQ. This satisfies "show the refund policy clearly before checkout."
- **Q-COUNSEL:** Is this policy compliant with MD digital-goods refund rules, or must the remedy be narrower/broader?

### #4 SALES TAX — Y/R → corrected and decided: no collection at launch
- **Call (corrects the brief):** Orbital Desk LLC is a **NY** LLC with no physical nexus in MD/VA/DC/PA/DE. Remote-seller thresholds (~$100k or 200 transactions/state) are orders of magnitude above launch volumes. **Decision: no sales-tax registration and no collection at launch; no Stripe Tax.** Re-evaluate when approaching 150 transactions or $75k in any single state, or annually — calendar note set.
- **Q-CPA:** Confirm NY treatment of PDF information products (not prewritten software) and the monitoring thresholds.

### #5 AI DISCLOSURE — Y → posture held, verified clean
- **Call:** Verified the storefront makes no "expert-designed," "professionally designed," or human-expert claims — the AI-deception risk the brief flagged is not present in the copy. David's standing no-public-AI-disclosure rule holds. Silence remains the position.
- **Q-COUNSEL:** Any AI-disclosure duty in MD/VA/DC/PA for static documents on our own storefront? **Q-DAVID (conditional):** if counsel says disclosure is required, that conflicts with your standing rule — your call then.

### #6 IMAGES — Y → verified clean, rule recorded
- **Call:** All storefront photos are David's own (public/images/). No county, CBT, or program logos anywhere — verified. Rule: never use program logos (implies endorsement); future assets are David's photos or licensed stock only.

### #7 PRIVACY — Y-low → policy published
- **Call:** `/privacy.html` is live and linked in every footer: email for delivery/receipts/support, order records, Stripe as payment processor (we never see card numbers), Cloudflare server logs, no sale of data, no marketing email currently, no tracking cookies of our own. MD MODPA (~35k-consumer threshold) is not triggered at launch volumes; the policy exists regardless.

### #8 CAN-SPAM — G → no action needed
- **Call:** The only email is transactional (download link, receipt, support) — no opt-out required. If marketing email ever starts: RA postal address (418 Broadway STE N, Albany, NY 12207) in the footer + working unsubscribe, opt-outs honored within 10 business days.

### #9 FTC REVIEWS — R if violated → verified clean, rule recorded
- **Call:** No reviews or testimonials appear anywhere on the storefront — verified. Standing rule: never publish AI-written, invented, bought, or gated reviews (16 CFR 465).
- **OPEN (Grok's lane):** ad-claims pass on "rebate-ready" and "done-for-you" as implied-approval claims, plus the hero's "Done for you" line. Not duplicated here.

### #10 ADA — Y → basics done, audit deferred
- **Call:** All images have alt text, the email input has an aria-label, all actions are real buttons, semantic HTML throughout. Full WCAG 2.1 AA audit deferred to post-launch.

## Pre-launch gates (brief's #1, #2, #4)
All three are now **mitigated pending counsel**: licensing framing + terms + FAQ are live; liability terms are live; the tax decision is documented. None of the three blocks continued test-mode work. Go-live still requires: (a) the 10 dual-approved PDFs with dated-edition footers, (b) counsel's answers on the Q-COUNSEL/Q-CPA items above, (c) Grok's ad-claims pass, (d) the domain pick + trademark knockout on "Rebate-Ready", (e) the fulfillment fixes (email delivery) already in flight.

## What changed on the storefront today
- New `/terms.html` (Terms of Sale, 10 sections) and `/privacy.html`, linked in every page footer.
- Every Buy card now shows "Digital download · Refund policy · Terms of Sale · Rebate approval is the county's decision" before checkout.
- FAQ: new "Are these professional landscape designs?" answer; refund answer now names the contact email and links the terms; contractor answer adds perc-test + call-811.
- Support contact published as support@rebatereadygarden.com (flagged below as changeable).

## Q-DAVID (your calls)
1. E&O / general-liability insurance before go-live, or launch without and revisit at revenue?
2. Support email: keep support@rebatereadygarden.com public on the store, or set up a dedicated address (e.g., support@<new domain>) once the domain is picked?
3. Conditional: if counsel requires AI disclosure, it conflicts with your no-disclosure rule — your call then.
