#!/bin/bash
# deploy.sh — one-command Rebate-Ready Garden production deploy + smoke check.
# The full wrangler invocation (token, project, branch) kept in exactly one place.
set -euo pipefail
cd "$(dirname "$0")"

echo "== deploying =="
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
