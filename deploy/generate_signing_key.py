"""Generate Ed25519 keypair for ACP bundle signing + publish to Secret Manager.

Per codex G11 P0.3 + P0.4: real Ed25519 signing, not placeholders. Private key
goes to GCP Secret Manager (never to git). Public key emitted in two encodings:
- multibase z-prefix for DID doc publicKeyMultibase (per W3C did:key / did:web spec)
- hex / base64 for human-readable reference

Run once during Phase 5 deploy setup. The output public key string is copy-pasted
into services/mesh_api/main.py DID_DOC.
"""
from __future__ import annotations

import base64
import json
import os
import subprocess
import sys

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization


PROJECT = "pawconscious-mesh-2026"
SECRET_NAME = "acp-bundle-signer-ed25519"


def b58encode(b: bytes) -> str:
    """Minimal base58btc encode (Bitcoin alphabet) for multibase z-prefix."""
    alphabet = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
    n = int.from_bytes(b, "big")
    out = ""
    while n > 0:
        n, r = divmod(n, 58)
        out = alphabet[r] + out
    # Leading zero bytes → leading '1's
    for byte in b:
        if byte == 0:
            out = "1" + out
        else:
            break
    return out


def main() -> None:
    # Generate Ed25519 keypair
    priv = Ed25519PrivateKey.generate()
    pub = priv.public_key()

    priv_pem = priv.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    pub_raw = pub.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )

    # multibase z-prefix = 'z' (base58btc) + multicodec(0xed01 = Ed25519) + raw public key
    multicodec_prefix = b"\xed\x01"
    pub_multicodec = multicodec_prefix + pub_raw
    pub_multibase = "z" + b58encode(pub_multicodec)

    print(f"PUBLIC_KEY_RAW_HEX     : {pub_raw.hex()}")
    print(f"PUBLIC_KEY_BASE64      : {base64.b64encode(pub_raw).decode()}")
    print(f"PUBLIC_KEY_MULTIBASE   : {pub_multibase}")
    print()

    # Store private key in Secret Manager (if --create-secret flag given)
    if "--create-secret" in sys.argv:
        # Try to create the secret; if exists, add new version
        create_result = subprocess.run(
            ["gcloud", "secrets", "create", SECRET_NAME, "--project", PROJECT,
             "--replication-policy=automatic"],
            capture_output=True, text=True,
        )
        if create_result.returncode != 0 and "already exists" not in create_result.stderr:
            print(f"ERROR creating secret: {create_result.stderr}", file=sys.stderr)
            sys.exit(1)

        add_version = subprocess.run(
            ["gcloud", "secrets", "versions", "add", SECRET_NAME,
             "--project", PROJECT, "--data-file=-"],
            input=priv_pem, capture_output=True,
        )
        if add_version.returncode != 0:
            print(f"ERROR adding version: {add_version.stderr.decode()}", file=sys.stderr)
            sys.exit(1)

        print(f"✅ Private key stored in Secret Manager: projects/{PROJECT}/secrets/{SECRET_NAME}")
        print()
        print("Next steps:")
        print("1. Grant runtime SA Secret Manager access (already done in deploy/sa-config.md)")
        print(f"2. Update services/mesh_api/main.py DID_DOC publicKeyMultibase = '{pub_multibase}'")
        print("3. Update mesh_api to load private key from Secret Manager + sign bundles")
    else:
        print("--- DRY RUN ---")
        print("To store private key in Secret Manager, re-run with --create-secret")


if __name__ == "__main__":
    main()
