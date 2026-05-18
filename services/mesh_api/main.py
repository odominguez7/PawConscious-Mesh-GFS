"""PawConscious Mesh — public A2A v0.3 endpoint + DID doc + verify_claim service.

FastAPI service exposing:
- GET  /.well-known/agent-card.json — A2A v0.3 agent card (public discovery)
- GET  /.well-known/did.json — DID doc for did:web:pawconscious.com (codex G10 #6)
- POST /a2a/v1/tasks/send — A2A protocol task endpoint (API-key gated per G7.3)
- GET  /pcec/v0/claim/{urn} — PCEC v0.1 resolver
- GET  /health — Cloud Run health probe

Demo API key gating per codex G7.3 P1.7 + G10 #4 — hackathon period only.
Public open access ships post-hackathon once abuse controls validated.

Per codex G10 #6 + #7: per-bundle hash + signature verification baked into
demo output; tamper-evident transparency log via hash chaining on Firestore (deferred
to Phase 5 deploy).
"""
from __future__ import annotations

import base64
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Any, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization
from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.responses import JSONResponse, PlainTextResponse
from pydantic import BaseModel, Field

from agents.orchestrator import run_mesh, summarize
from shared.pcec_schema import EndorsementClaimBundle


DEMO_API_KEY = os.environ.get("ACP_DEMO_API_KEY", "demo-key-2026-06")
SERVICE_VERSION = "0.1.0"

# Real Ed25519 public key — generated 2026-05-18, private in GCP Secret Manager
# acp-bundle-signer-ed25519 (project pawconscious-mesh-2026)
# Per codex G11 P0.3 — no placeholder
SIGNER_PUBLIC_KEY_MULTIBASE = "z6MkfYpcbqZEdKKKg6qdNb3kpa1z5kTE27XaujSdp56CoBkZ"
SIGNER_PUBLIC_KEY_HEX = "10486ac1a48c4f6731e36115b0e4e3fe5b92a587c88c7ede9677bf4feaab48c6"
SIGNER_DID = "did:web:pawconscious.com#owner"
SIGNING_SECRET_RESOURCE = (
    "projects/pawconscious-mesh-2026/secrets/acp-bundle-signer-ed25519/versions/latest"
)


app = FastAPI(
    title="PawConscious Mesh — ACP v0.1",
    version=SERVICE_VERSION,
    description="Agentic Compliance Protocol reference deployment for pet supplements. "
                "Public A2A v0.3 mesh endpoint. Submit pet product URLs for evidence verification.",
)


# ---------------------------------------------------------------------------
# Public well-known endpoints
# ---------------------------------------------------------------------------

A2A_AGENT_CARD = {
    "name": "PawConscious Mesh",
    "description": (
        "A2A trust mesh for expert-claim commerce. Verify endorsement claims on commerce "
        "SKUs against signed PCEC v0.1 evidence bundles. Pet supplement reference deployment."
    ),
    "url": "https://mesh.pawconscious.com/a2a/v1",  # populates after Phase 5 deploy
    "version": SERVICE_VERSION,
    "provider": {
        "organization": "PawConscious",
        "url": "https://pawconscious.com",
    },
    "documentationUrl": "https://github.com/odominguez7/PawConscious-Mesh-GFS",
    "capabilities": {
        "streaming": False,
        "pushNotifications": False,
        "stateTransitionHistory": False,
    },
    "authentication": {
        "schemes": ["api-key"],
        "note": (
            "Hackathon period: demo API key required (header: X-API-Key). "
            "Public open access ships post-hackathon once abuse controls validated. "
            "Issued by: PawConscious (sole operator, single trust root in v0.1)."
        ),
    },
    "defaultInputModes": ["text", "application/json"],
    "defaultOutputModes": ["application/ld+json", "text"],
    "skills": [
        {
            "id": "verify_claim",
            "name": "Verify endorsement claim",
            "description": (
                "Given a product URL, run the full mesh pipeline (5 specialized ADK agents on "
                "Google Cloud) and return a signed PCEC v0.1 evidence bundle with vet-rubric "
                "scoring, FTC §255 mapping, and adversarial audit verdict."
            ),
            "tags": ["trust", "endorsement", "substantiation", "pet-supplements", "PCEC"],
            "examples": [
                "Verify https://www.nativepet.com/products/hip-joint",
            ],
            "inputModes": ["text"],
            "outputModes": ["application/ld+json"],
        },
        {
            "id": "fetch_substantiation_bundle",
            "name": "Fetch substantiation bundle by URN",
            "description": (
                "Given a PCEC claim URN (urn:pcec:claim:...), return the full bundle including "
                "EvidenceBundle + VetRubricScore + ComplianceMapping + AuditVerdict objects."
            ),
            "tags": ["PCEC", "evidence", "audit"],
            "inputModes": ["text"],
            "outputModes": ["application/ld+json"],
        },
    ],
}


DID_DOC = {
    "@context": [
        "https://www.w3.org/ns/did/v1",
        "https://w3id.org/security/suites/ed25519-2020/v1",
    ],
    "id": "did:web:pawconscious.com",
    "verificationMethod": [
        {
            "id": "did:web:pawconscious.com#owner",
            "type": "Ed25519VerificationKey2020",
            "controller": "did:web:pawconscious.com",
            "publicKeyMultibase": SIGNER_PUBLIC_KEY_MULTIBASE,
        },
    ],
    "authentication": ["did:web:pawconscious.com#owner"],
    "assertionMethod": ["did:web:pawconscious.com#owner"],
    "service": [
        {
            "id": "did:web:pawconscious.com#pcec-resolver",
            "type": "PCECResolver",
            "serviceEndpoint": "https://mesh.pawconscious.com/pcec/v0",
        },
        {
            "id": "did:web:pawconscious.com#a2a-mesh",
            "type": "A2AMeshEndpoint",
            "serviceEndpoint": "https://mesh.pawconscious.com/a2a/v1",
        },
    ],
}


@app.get("/health")
async def health() -> dict[str, Any]:
    return {"status": "ok", "service": "pawconscious-mesh", "version": SERVICE_VERSION}


@app.get("/.well-known/agent-card.json")
async def agent_card() -> dict[str, Any]:
    """A2A v0.3 public agent card. Discoverable by any A2A-compatible client."""
    return A2A_AGENT_CARD


@app.get("/.well-known/did.json")
async def did_doc() -> dict[str, Any]:
    """DID document for did:web:pawconscious.com (codex G10 #6)."""
    return DID_DOC


# ---------------------------------------------------------------------------
# A2A v0.3 task endpoint
# ---------------------------------------------------------------------------

class A2ATaskRequest(BaseModel):
    """A2A v0.3 task envelope. Simplified for v0.1; full spec compliance in Phase 5."""
    skill: str = Field(..., description="Skill ID per agent card")
    input: dict[str, Any] = Field(..., description="Skill input arguments")
    task_id: Optional[str] = None


class A2ATaskResponse(BaseModel):
    task_id: str
    status: str
    output: dict[str, Any]
    bundle_hash: str
    bundle_signature_placeholder: str = ""  # populated with real ed25519 sig at runtime


def compute_bundle_hash(bundle: EndorsementClaimBundle) -> str:
    """Per codex G10 #7 — per-bundle hash for integrity verification."""
    canonical = bundle.model_dump_json(exclude={"signature"}, indent=None)
    return "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()


@lru_cache(maxsize=1)
def _load_signer() -> Optional[Ed25519PrivateKey]:
    """Load Ed25519 private key from Secret Manager (or local file fallback for dev).

    Caches in-process. Returns None if unavailable (signature will be marked as 'unsigned'
    so we never silently fake a sig).
    """
    # Try local dev file first (never committed; in .gitignore via keys/*)
    local_key = os.environ.get("ACP_SIGNING_KEY_PEM_PATH")
    if local_key and os.path.exists(local_key):
        with open(local_key, "rb") as f:
            pem = f.read()
        return serialization.load_pem_private_key(pem, password=None)  # type: ignore

    # Secret Manager fetch (only works when deployed with proper SA + ADC)
    try:
        from google.cloud import secretmanager
        client = secretmanager.SecretManagerServiceClient()
        response = client.access_secret_version(request={"name": SIGNING_SECRET_RESOURCE})
        pem = response.payload.data
        return serialization.load_pem_private_key(pem, password=None)  # type: ignore
    except Exception as e:
        print(f"[mesh_api] WARN: signer load failed: {e}. Bundles will be marked unsigned.")
        return None


def sign_bundle(bundle: EndorsementClaimBundle) -> str:
    """Real Ed25519 signature over the canonical bundle JSON (codex G11 P0.4)."""
    signer = _load_signer()
    if signer is None:
        return f"unsigned (no signer available); bundle_hash={compute_bundle_hash(bundle)}"
    canonical = bundle.model_dump_json(exclude={"signature"}, indent=None).encode("utf-8")
    sig = signer.sign(canonical)
    sig_b64 = base64.b64encode(sig).decode("ascii")
    return f"ed25519:{SIGNER_DID}:{sig_b64}"


@app.post("/a2a/v1/tasks/send", response_model=A2ATaskResponse)
async def a2a_send(
    request: A2ATaskRequest,
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
) -> A2ATaskResponse:
    """A2A v0.3 task entry. Demo-key gated per codex G7.3 P1.7."""
    if x_api_key != DEMO_API_KEY:
        raise HTTPException(status_code=401, detail="X-API-Key required. Request via GitHub issue.")

    if request.skill == "verify_claim":
        product_url = request.input.get("product_url") or request.input.get("sku") or request.input.get("url")
        if not product_url:
            raise HTTPException(status_code=400, detail="Missing product_url / sku / url in input")
        max_claims = int(request.input.get("max_claims", 3))  # default tight for demo latency
        bundle = await run_mesh(product_url, max_claims=max_claims)
        bundle_hash = compute_bundle_hash(bundle)
        bundle.signature = sign_bundle(bundle)  # real Ed25519 sig per codex G11 P0.4
        return A2ATaskResponse(
            task_id=request.task_id or f"task-{datetime.now(timezone.utc).isoformat()}",
            status="completed",
            output=json.loads(bundle.model_dump_json()),
            bundle_hash=bundle_hash,
            bundle_signature_placeholder=bundle.signature,
        )

    raise HTTPException(status_code=404, detail=f"Unknown skill: {request.skill}")


# ---------------------------------------------------------------------------
# PCEC v0 resolver (stub — real implementation in Phase 5 with Firestore)
# ---------------------------------------------------------------------------

@app.get("/pcec/v0/claim/{urn}")
async def resolve_claim(urn: str) -> dict[str, Any]:
    """PCEC v0.1 resolver — returns signed bundle by URN. Phase 5 wires Firestore."""
    return {
        "urn": urn,
        "status": "not_implemented_in_v0.1_local",
        "note": (
            "v0.1 resolver requires Firestore-backed transparency log (Phase 5 Cloud Run deployment). "
            "For local testing, call POST /a2a/v1/tasks/send to issue + receive a bundle in one call."
        ),
    }


# ---------------------------------------------------------------------------
# Root index
# ---------------------------------------------------------------------------

@app.get("/", response_class=PlainTextResponse)
async def root() -> str:
    return (
        "PawConscious Mesh — ACP v0.1\n\n"
        "Public endpoints:\n"
        "  GET  /.well-known/agent-card.json   A2A v0.3 agent card\n"
        "  GET  /.well-known/did.json          DID document\n"
        "  POST /a2a/v1/tasks/send             A2A task endpoint (X-API-Key required)\n"
        "  GET  /pcec/v0/claim/{urn}           PCEC v0.1 resolver\n"
        "  GET  /health                        Health probe\n\n"
        "Repo: https://github.com/odominguez7/PawConscious-Mesh-GFS\n"
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.environ.get("PORT", "8080")), reload=False)
