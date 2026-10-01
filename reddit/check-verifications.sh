#!/bin/bash
# Check orbitdesk.ops@gmail.com for recent verification-code emails.
# Prints sender + arrival time only — never code values.
# Usage: check-verifications.sh
ACCT="c5c473e0037f4d2da8f4b59f6f8e592e"
hatch_gws_cli gmail +triage --account "$ACCT" \
  --query '(from:reddit OR from:x.com OR from:facebook OR from:instagram) newer_than:2d' \
  --max 10 --format json 2>/dev/null | \
  python3 -c "
import json,sys
try:
    d=json.load(sys.stdin)
except Exception:
    print('no results'); sys.exit()
msgs=d.get('messages',d if isinstance(d,list) else [])
for m in msgs:
    print(f\"{m.get('date','?')} | {m.get('from','?')[:60]} | {m.get('subject','?')[:70]}\")
if not msgs: print('no verification emails in last 2 days')
"
