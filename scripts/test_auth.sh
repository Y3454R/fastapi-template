#!/usr/bin/env bash
set -euo pipefail

# scripts/test_auth.sh
# Simple auth tester: logs in and calls a protected endpoint.

HOST=${HOST:-http://localhost:8298}
API_PREFIX=${API_PREFIX:-/api/v1}
EMAIL=${EMAIL:-[EMAIL_ADDRESS]}
PASSWORD=${PASSWORD:-[PASSWORD]}

echo "Logging in as $EMAIL -> $HOST$API_PREFIX/auth/login"
RESP=$(curl -s -X POST "$HOST$API_PREFIX/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\"}")

ACCESS_TOKEN=$(echo "$RESP" | python3 -c 'import sys,json
try:
    d=json.load(sys.stdin)
    print(d.get("access_token",""))
except Exception:
    print("")')

if [ -z "$ACCESS_TOKEN" ]; then
  echo "Failed to obtain access_token. Full response:" >&2
  echo "$RESP" >&2
  exit 1
fi

echo "Obtained access token. Calling protected endpoint: $API_PREFIX/auth/me"
curl -s -H "Authorization: Bearer $ACCESS_TOKEN" "$HOST$API_PREFIX/auth/me" | python3 -m json.tool

echo "Done."
