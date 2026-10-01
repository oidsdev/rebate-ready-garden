#!/bin/bash
# deploy.sh — one-command Rebate-Ready Garden production deploy pipeline (audit P1).
# gen.py -> data QA -> price check -> commit -> wrangler deploy -> smoke check.
# Fails loudly at the first broken step; never deploys without the gates passing.
set -euo pipefail
cd "$(dirname "$0")"

echo "== 1/5 regenerate catalog =="
python3 gen.py

echo "== 2/5 data QA =="
python3 check-data-qa.py

echo "== 3/5 price consistency =="
python3 check-prices.py

echo "== 4/5 commit =="
git add -A
if git diff --cached --quiet; then
  echo "no changes to commit"
else
  git commit -m "deploy $(date -u +%Y-%m-%dT%H:%MZ)"
fi

echo "== 5/5 deploy =="
CLOUDFLARE_API_TOKEN=$(cat ~/.cloudflare/api-token) \
/opt/hatch-image/bin/npx --yes wrangler pages deploy public \
  --project-name=rebate-ready-garden --branch=main 2>&1 | tail -3

echo "== smoke check =="
sleep 5
for url in "https://rebatereadygarden.com/" "https://rebatereadygarden.com/rebate-database.html"; do
  code=$(curl -s -o /dev/null -w "%{http_code}" -L --max-time 20 "$url")
  echo "$code  $url"
  [ "$code" = "200" ] || { echo "SMOKE CHECK FAILED: $url -> $code" >&2; exit 1; }
done
echo "deploy OK"
