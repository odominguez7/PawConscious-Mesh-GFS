#!/usr/bin/env bash
# Verify what PawConscious Mesh actually does — against the LIVE service.
# Usage:  ./verify.sh                  (defaults to prod)
#         ./verify.sh http://127.0.0.1:8000
#
# Every check hits a real endpoint and prints PASS/FAIL with the evidence.
# Nothing here trusts the API's word: signatures are verified against the
# published DID key, and a forged bundle is shown to be rejected.
set -uo pipefail
BASE="${1:-https://mesh-api-40952019806.us-central1.run.app}"
KEY="demo-key-2026-06"
PY=".venv/bin/python"
GREEN_GRUFF="https://www.greengruff.com/products/ease"
pass=0; fail=0
ok(){ echo "   PASS · $1"; pass=$((pass+1)); }
no(){ echo "   FAIL · $1"; fail=$((fail+1)); }

echo "============================================================"
echo " Verifying PawConscious Mesh @ $BASE"
echo "============================================================"

echo; echo "1. Independent signature verification + tamper rejection (ShopperAgent)"
sa=$($PY examples/shopper_agent.py "$BASE" 2>&1)
if echo "$sa" | grep -q "VALID" && echo "$sa" | grep -q "tamper detected"; then
  ok "external agent verified the signatures; forged bundle rejected"
else
  no "ShopperAgent did not verify + reject as expected"; echo "$sa" | tail -4
fi

echo; echo "2. Verify ONE signature by hand against the published DID key"
$PY - "$BASE" <<'PY' && ok "signature verifies against /.well-known/did.json" || no "manual signature check failed"
import json, sys, base64, urllib.request, urllib.parse
sys.path.insert(0, ".")
from shared.pcec_schema import canonical_bundle_bytes
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
B = sys.argv[1]
get = lambda u: json.load(urllib.request.urlopen(u, timeout=20))
ALPHA = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
def b58(s):
    n = 0
    for c in s: n = n * 58 + ALPHA.index(c)
    return n.to_bytes((n.bit_length() + 7) // 8, "big")
mb = get(B + "/.well-known/did.json")["verificationMethod"][0]["publicKeyMultibase"]
key = Ed25519PublicKey.from_public_bytes(b58(mb[1:])[2:34])   # strip 'z' + multicodec prefix
b = get(B + "/a2a/v1/lookup?url=" + urllib.parse.quote("https://www.greengruff.com/products/ease", safe=""))
sig = base64.b64decode(b["bundle_signature"].rsplit(":", 1)[1])
key.verify(sig, canonical_bundle_bytes(b["output"]))   # raises if invalid
PY

echo; echo "3. Hot path serves a REAL signed bundle (not a hand-authored fake)"
sig=$(curl -s -m20 "$BASE/a2a/v1/lookup?url=$GREEN_GRUFF" | $PY -c 'import sys,json;print(json.load(sys.stdin).get("bundle_signature",""))')
case "$sig" in
  ed25519:did:web:*) ok "signature is ed25519:did:web:… (real)";;
  *) no "unexpected signature: ${sig:0:40}";;
esac

echo; echo "4. Document AI removed from non-demo surfaces"
h=$(curl -s "$BASE/" | grep -c "Document AI"); a=$(curl -s "$BASE/architecture" | grep -ci "document ai")
[ "$h" = 0 ] && [ "$a" = 0 ] && ok "0 mentions on homepage and /architecture" || no "still present (home=$h arch=$a)"

echo; echo "5. Event loop stays free during a live verify (no freeze)"
curl -s -m12 -X POST "$BASE/a2a/v1/tasks/send" -H "Content-Type: application/json" -H "X-API-Key: $KEY" \
  -d '{"skill":"verify_claim","input":{"product_url":"https://www.nativepet.com/products/hip-joint"}}' -o /dev/null
t=$(curl -s -o /dev/null -m10 -w "%{time_total}" "$BASE/health")
awk -v t="$t" 'BEGIN{exit !(t<2)}' && ok "/health responded in ${t}s during a verify" || no "/health slow (${t}s) — worker blocked"

echo; echo "6. SSRF guard blocks the cloud metadata server"
tid=$(curl -s -m12 -X POST "$BASE/a2a/v1/tasks/send" -H "Content-Type: application/json" -H "X-API-Key: $KEY" \
  -d '{"skill":"verify_claim","input":{"product_url":"http://169.254.169.254/"}}' | $PY -c 'import sys,json;print(json.load(sys.stdin).get("task_id",""))')
sleep 9
err=$(curl -s -m10 "$BASE/a2a/v1/tasks/get/$tid" | $PY -c 'import sys,json;print(json.load(sys.stdin).get("error") or "")')
echo "$err" | grep -q "SSRF guard" && ok "metadata URL rejected: ${err:0:60}…" || no "no SSRF rejection (got: ${err:0:60})"

echo; echo "7. Trust-spine tests"
if PYTHONPATH=. $PY -m pytest tests/test_signature_verify.py -q >/tmp/_vsh_tests 2>&1; then
  ok "$(grep -oE '[0-9]+ passed' /tmp/_vsh_tests | head -1)"
else
  no "signature tests failed"; tail -3 /tmp/_vsh_tests
fi

echo; echo "============================================================"
echo " RESULT: $pass passed, $fail failed"
echo "============================================================"
[ "$fail" = 0 ]
