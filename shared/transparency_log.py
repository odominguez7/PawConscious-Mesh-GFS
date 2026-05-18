"""Firestore-backed PCEC transparency log (Phase 11 + G19 amendments).

Per codex G10 #4 + G17 #2 + G18 #6 + G19 #3 #6: an append-only log of issued
bundles. Documents are keyed by URN. Each document carries the full bundle, its
signature, hash, issued_at, and a prev_hash plus chain_anchor for tamper
evident chaining.

G19 amendments (2026-05-18):
- append() runs inside a Firestore transaction: read _chain_head, write claim
  doc, write new _chain_head, all atomic. Prevents fork-under-concurrent-writes.
- get_head_anchor() exposed for callers that want the head at submit time
  (so the 202 response can return head_anchor_at_submit).
- append() is idempotent on URN: if the URN already exists, return the stored
  entry instead of double-writing. (The mesh-api layer also gates by
  Idempotency-Key but URN-level idempotency is the last line of defense.)

Public read. Authenticated write (mesh-api runtime SA only).
"""
from __future__ import annotations

import asyncio
import base64
import hashlib
from typing import Any, Optional

PROJECT = "pawconscious-mesh-2026"
COLLECTION = "acp-claims"
META_COLLECTION = "acp-claims-meta"
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
    """Firestore-backed append-only transparency log with transactional append."""

    def __init__(self, project: str = PROJECT):
        from google.cloud import firestore
        self._client = firestore.Client(project=project)
        self._collection = self._client.collection(COLLECTION)
        self._head_ref = self._client.collection(META_COLLECTION).document(HEAD_DOC)

    def get_head_anchor(self) -> Optional[str]:
        """Public read of the current chain head anchor (used at submit time)."""
        snap = self._head_ref.get()
        if not snap.exists:
            return None
        return snap.to_dict().get("prev_hash")

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
        """Append a new bundle to the log inside a Firestore transaction.

        Atomicity guarantees (G19 #3):
        1. Read _chain_head inside transaction
        2. If URN already exists, return existing entry (idempotent)
        3. Write claim doc + new _chain_head atomically

        Two concurrent verify_claim runs cannot fork the chain or lose updates.
        """
        from google.cloud import firestore

        claim_ref = self._collection.document(urn)
        head_ref = self._head_ref

        @firestore.transactional
        def _txn(transaction: "firestore.Transaction") -> dict[str, Any]:
            existing_snap = claim_ref.get(transaction=transaction)
            if existing_snap.exists:
                return existing_snap.to_dict()

            head_snap = head_ref.get(transaction=transaction)
            prev_hash = head_snap.to_dict().get("prev_hash") if head_snap.exists else None

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
            chain_payload = f"{bundle_hash}:{prev_hash or 'genesis'}".encode("utf-8")
            entry["chain_anchor"] = "sha256:" + hashlib.sha256(chain_payload).hexdigest()

            transaction.set(claim_ref, entry)
            transaction.set(
                head_ref,
                {"prev_hash": entry["chain_anchor"], "updated_at": _utc_now()},
            )
            return entry

        transaction = self._client.transaction()
        return _txn(transaction)

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


async def get_head_anchor_async() -> Optional[str]:
    return await asyncio.to_thread(get_log().get_head_anchor)
