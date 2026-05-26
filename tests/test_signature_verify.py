"""Trust-spine tests: a bundle signed by the server must verify for any
external party, and a tampered bundle must NOT. This is the literal claim of
the product ("don't trust us, verify the signature"), and it was previously
untested. Regression guard for two real bugs:

  1. canonical canonicalization must be transport-stable (Pydantic
     model_dump_json field order is NOT reproducible after a JSON round-trip).
  2. bundle_urn is set AFTER hashing/signing, so it must be excluded from the
     canonical or signed bytes (urn absent) won't match served bytes (urn set).
"""
import base64
import hashlib
import json

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from shared.pcec_schema import EndorsementClaimBundle, canonical_bundle_bytes

# Minimal real-shaped bundle (mirrors a mesh output).
_BUNDLE = {
    "sku": "https://example.com/p",
    "product_url": "https://example.com/p",
    "claims": [{"text": "Supports joints", "kind": "efficacy", "position_on_page": "hero", "raw_context": "x"}],
    "evidence": [],
    "vet_scores": [],
    "compliance": [],
    "audit": [{"claim": {"text": "Supports joints", "kind": "efficacy", "position_on_page": "hero", "raw_context": "x"},
               "verdict": "FAIL", "challenges_run": [], "findings": [], "auditor_agent": "did:web:x:auditor"}],
    "issued_at": "2026-05-26T17:13:50.117271",
    "issuer": "did:web:example",
}


def _server_sign(bundle: EndorsementClaimBundle, sk: Ed25519PrivateKey):
    """Reproduce the server ordering: hash + sign, THEN set bundle_urn."""
    from shared.pcec_schema import EndorsementClaimBundle as _B  # noqa
    bundle.bundle_urn = None
    bundle.signature = None
    h = "sha256:" + hashlib.sha256(canonical_bundle_bytes(bundle)).hexdigest()
    sig = sk.sign(canonical_bundle_bytes(bundle))
    bundle.bundle_urn = "urn:pcec:claim:" + h[7:25]  # set AFTER signing
    bundle.signature = "ed25519:did:web:example#owner:" + base64.b64encode(sig).decode()
    return sig, json.loads(bundle.model_dump_json())  # served output shape


def test_canonical_is_transport_stable():
    out = json.loads(EndorsementClaimBundle(**_BUNDLE).model_dump_json())
    assert canonical_bundle_bytes(out) == canonical_bundle_bytes(json.loads(json.dumps(out)))


def test_signature_verifies_after_transport():
    sk = Ed25519PrivateKey.generate()
    sig, served = _server_sign(EndorsementClaimBundle(**_BUNDLE), sk)
    # external verifier reproduces the signed bytes from the served bundle alone
    sk.public_key().verify(sig, canonical_bundle_bytes(served))  # raises if invalid


def test_tampered_bundle_fails_verification():
    sk = Ed25519PrivateKey.generate()
    sig, served = _server_sign(EndorsementClaimBundle(**_BUNDLE), sk)
    served["audit"][0]["verdict"] = "PASS"  # forge a pass
    try:
        sk.public_key().verify(sig, canonical_bundle_bytes(served))
        assert False, "tampered bundle must not verify"
    except InvalidSignature:
        pass


def test_bundle_urn_excluded_from_canonical():
    out = json.loads(EndorsementClaimBundle(**_BUNDLE).model_dump_json())
    out["bundle_urn"] = "urn:pcec:claim:anything"
    c1 = canonical_bundle_bytes(out)
    out["bundle_urn"] = "urn:pcec:claim:totally-different"
    assert c1 == canonical_bundle_bytes(out), "bundle_urn must not affect the signed bytes"
