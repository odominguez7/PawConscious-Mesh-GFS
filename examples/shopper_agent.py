#!/usr/bin/env python3
"""ShopperAgent — a REAL external A2A consumer for PawConscious.

This is the buyer side of the trust layer: an independent agent that decides
whether to recommend a product to its user. It does NOT trust PawConscious's
say-so. It:

  1. Discovers the public agent card   GET /.well-known/agent-card.json
  2. Fetches the issuer's public key   GET /.well-known/did.json
  3. Looks up a brand's signed bundle  GET /a2a/v1/lookup?url=...
  4. INDEPENDENTLY verifies the Ed25519 signature against that public key,
     by re-deriving the exact signed bytes from the bundle.
  5. Only then makes a RECOMMEND / SKIP decision from the verified verdict.

Then it runs a TAMPER TEST: it mutates one field of a verified bundle and
re-verifies. The signature flips to INVALID and the agent SKIPs — proving the
decision rests on cryptography, not on trusting the API response.

Run (from repo root):  python examples/shopper_agent.py
Point elsewhere:        python examples/shopper_agent.py https://mesh-api-...run.app

No human in the loop. No "trust me". Just A2A discovery + Ed25519.
"""
from __future__ import annotations

import copy
import json
import sys
import urllib.parse
import urllib.request
from pathlib import Path

# The agent re-derives the signed bytes with the SAME model the issuer signed,
# so it imports the public PCEC schema from the repo. (A third party would
# vendor the published schema; same bytes either way.)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from shared.pcec_schema import canonical_bundle_bytes  # noqa: E402

from cryptography.exceptions import InvalidSignature  # noqa: E402
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey  # noqa: E402

DEFAULT_BASE = "https://mesh-api-40952019806.us-central1.run.app"
BRANDS = [
    "https://www.cosequin.com/product/cosequin-maximum-strength-plus-msm-chewable-tablets/",
    "https://www.greengruff.com/products/ease",
    "https://www.justfoodfordogs.com/product/calming-chews-for-dogs/50020180.html",
]

_B58 = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"


def _b58decode(s: str) -> bytes:
    n = 0
    for ch in s:
        n = n * 58 + _B58.index(ch)
    full = n.to_bytes((n.bit_length() + 7) // 8, "big")
    pad = len(s) - len(s.lstrip("1"))
    return b"\x00" * pad + full


def did_key_to_pubkey(multibase: str) -> Ed25519PublicKey:
    """did:key multibase (z...) -> Ed25519 public key. 'z' = base58btc; the
    decoded bytes are multicodec 0xed01 (ed25519-pub) + the 32-byte raw key."""
    assert multibase.startswith("z"), f"expected base58btc multibase, got {multibase[:4]!r}"
    raw = _b58decode(multibase[1:])
    assert raw[:2] == b"\xed\x01", f"expected ed25519-pub multicodec, got {raw[:2].hex()}"
    return Ed25519PublicKey.from_public_bytes(raw[2:34])


def _get(url: str) -> dict:
    with urllib.request.urlopen(url, timeout=20) as r:
        return json.loads(r.read())


def verify_signature(output: dict, signature: str, pubkey: Ed25519PublicKey) -> bool:
    """Re-derive the exact signed bytes and check the Ed25519 signature.

    The issuer signs `bundle.model_dump_json(exclude={'signature'})`. We rebuild
    that from the received bundle, so verification depends ONLY on the public key
    and the bundle contents — never on the server's claimed verdict.
    """
    import base64
    canonical = canonical_bundle_bytes(output)  # same transport-stable bytes the issuer signed
    sig_b64 = signature.rsplit(":", 1)[1]  # ed25519:<did>:<base64sig>
    try:
        pubkey.verify(base64.b64decode(sig_b64), canonical)
        return True
    except InvalidSignature:
        return False


def decide(verdict: str, flags: list) -> str:
    if verdict == "FAIL":
        return "SKIP   (a claim failed verification)"
    if verdict == "CONDITIONAL" or flags:
        return "RECOMMEND WITH CAVEAT (compliance flags present)"
    return "RECOMMEND"


def main() -> int:
    base = sys.argv[1].rstrip("/") if len(sys.argv) > 1 else DEFAULT_BASE
    print(f"\nShopperAgent → {base}\n" + "=" * 64)

    card = _get(f"{base}/.well-known/agent-card.json")
    skills = [s.get("id") or s.get("name") for s in card.get("skills", [])]
    print(f"1. discovered agent card: {card.get('name')} · skills={skills}")

    did = _get(f"{base}/.well-known/did.json")
    vm = did["verificationMethod"][0]
    pubkey = did_key_to_pubkey(vm["publicKeyMultibase"])
    print(f"2. fetched issuer public key: {vm['publicKeyMultibase'][:24]}…\n")

    last_good = None
    forge_target = None
    for url in BRANDS:
        b = _get(f"{base}/a2a/v1/lookup?url={urllib.parse.quote(url, safe='')}")
        if b.get("status") != "completed":
            print(f"   {url}\n     not cached (cold path) — skipping\n")
            continue
        out = b["output"]
        valid = verify_signature(out, b["bundle_signature"], pubkey)
        audit = [a.get("verdict") for a in out.get("audit", [])]
        verdict = "FAIL" if "FAIL" in audit else ("CONDITIONAL" if "CONDITIONAL" in audit else "PASS")
        flags = [c.get("ftc_section") for c in out.get("compliance", []) if c.get("violation_flag")]
        print(f"   {b.get('product_label')}")
        print(f"     signature : {'VALID ✅ (Ed25519, issuer DID key)' if valid else 'INVALID ❌'}")
        if not valid:
            print("     decision  : SKIP (cannot trust an unverifiable bundle)\n")
            continue
        print(f"     verdict   : {verdict}{' · flags ' + str(flags) if flags else ''}")
        print(f"     decision  : {decide(verdict, flags)}\n")
        last_good = (b, out)
        if verdict == "FAIL" and forge_target is None:
            forge_target = (b, out)  # the meaningful forgery: turn a FAIL into a PASS

    # TAMPER TEST — the proof that the decision rests on crypto, not the API.
    target = forge_target or last_good
    if target:
        b, out = target
        label = b.get("product_label")
        print("-" * 64)
        print(f"TAMPER TEST · forge {label}'s verdict to PASS, keep the original signature:")
        tampered = copy.deepcopy(out)
        for a in tampered.get("audit", []):
            a["verdict"] = "PASS"  # forge every failed/conditional verdict to PASS
        valid = verify_signature(tampered, b["bundle_signature"], pubkey)
        print(f"   signature : {'VALID ✅ (forgery undetected!)' if valid else 'INVALID ❌ (tamper detected)'}")
        print(f"   decision  : {'RECOMMEND' if valid else 'SKIP — forged bundle rejected'}")
        print("=" * 64)
        print("A forged verdict does not verify against the issuer key. The agent's"
              "\ntrust comes from the signature, not from anything PawConscious says.\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
