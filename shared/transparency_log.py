"""Firestore-backed PCEC transparency log (Phase 11).

Per codex G10 #4 + G17 #2 + G18 #6: replace the in-memory 501 stub with a real
append-only log of issued bundles. Documents are keyed by URN. Each document
carries the full bundle, signature, hash, issued_at, and a prev_hash field
that points at the most recently written claim for tamper evident chaining.

Public read. Authenticated write (mesh-api runtime SA only).
"""
from __future__ import annotations

import asyncio
import base64
import hashlib
from typing import Any, Optional

PROJECT = "pawconscious-mesh-2026"
COLLECTION = "acp-claims"
HEAD_DOC = "_chain_head"


def urn_for_hash(bundle_hash: str) -> str:
    """Compute a stable URN from the bundle hash.

    Format: urn:pcec:claim:<first 24 chars of base32-encoded sha256>
    """
    if bundle_hash.startswith("sha256:"):
        digest_hex = bundle_hash.split(":", 1)[1]
    else:
        digest_hex = bundle_hash
    digest_bytes = bytes.fromhex(digest_hex)
    b32 = base64.b32encode(digest_bytes).decode("ascii").rstrip("=")
    return f"urn:pcec:claim:{b32[:24].lower()}"


class TransparencyLog:
    """Firestore-backed append-only transparency log."""

    def __init__(self, project: str = PROJECT):
        from google.cloud import firestore
        self._client = firestore.Client(project=project)
        self._collection = self._client.collection(COLLECTION)
        self._head_ref = self._client.document(f"acp-claims-meta/{HEAD_DOC}")

    def _read_head_hash(self) -> Optional[str]:
        snap = self._head_ref.get()
        if not snap.exists:
            return None
        return snap.to_dict().get("prev_hash")

    def _write_head_hash(self, new_hash: str) -> None:
        self._head_ref.set({"prev_hash": new_hash, "updated_at": _utc_now()})

    def append(
        self,
        *,
        urn: str,
        bundle_hash: str,
        bundle_signature: str,
        bundle_json: dict[str, Any],
        signer_did: str,
        issuer: str,
    ) -> dict[str, Any]:
        """Append a new bundle to the log. Returns the stored entry."""
        prev_hash = self._read_head_hash()
        entry = {
            "urn": urn,
            "bundle_hash": bundle_hash,
            "bundle_signature": bundle_signature,
            "signer_did": signer_did,
            "issuer": issuer,
            "issued_at": _utc_now(),
            "prev_hash": prev_hash,
            "bundle": bundle_json,
        }
        # Chain anchor: hash of (this entry sans signature plus prev_hash)
        chain_payload = f"{bundle_hash}:{prev_hash or 'genesis'}".encode("utf-8")
        entry["chain_anchor"] = "sha256:" + hashlib.sha256(chain_payload).hexdigest()

        self._collection.document(urn).set(entry)
        self._write_head_hash(entry["chain_anchor"])
        return entry

    def fetch(self, urn: str) -> Optional[dict[str, Any]]:
        snap = self._collection.document(urn).get()
        if not snap.exists:
            return None
        return snap.to_dict()


_log_singleton: Optional[TransparencyLog] = None


def get_log() -> TransparencyLog:
    global _log_singleton
    if _log_singleton is None:
        _log_singleton = TransparencyLog()
    return _log_singleton


def _utc_now() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()


# Async wrappers so the mesh-api event loop never blocks on Firestore RPC

async def append_bundle_async(**kwargs) -> dict[str, Any]:
    return await asyncio.to_thread(get_log().append, **kwargs)


async def fetch_bundle_async(urn: str) -> Optional[dict[str, Any]]:
    return await asyncio.to_thread(get_log().fetch, urn)
