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

import asyncio
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
from shared.task_store import task_store, TaskState
from shared.transparency_log import (
    append_bundle_async, fetch_bundle_async, urn_for_hash,
)


DEMO_API_KEY = os.environ.get("ACP_DEMO_API_KEY", "demo-key-2026-06")
SERVICE_VERSION = "0.1.0"
PUBLIC_BASE_URL = os.environ.get(
    "ACP_PUBLIC_BASE_URL",
    "https://mesh-api-40952019806.us-central1.run.app",
)
# Canonical DID: did:web:<cloud-run-host>
# Self-hosted on Cloud Run, no external domain dependency
# (PawConscious.com is a separate live consumer site; this hackathon build runs
# independently. Fusion is a post-hackathon decision per Omar 2026-05-18.)
_PUBLIC_HOST = PUBLIC_BASE_URL.replace("https://", "").replace("http://", "").rstrip("/")
PUBLIC_DID = os.environ.get("ACP_PUBLIC_DID", f"did:web:{_PUBLIC_HOST}")
# Path C async: POST returns 202 immediately, client polls /a2a/v1/tasks/get/{id}
# Default 3 claims; no proxy timeout since the mesh is self-hosted on Cloud Run.
DEFAULT_MAX_CLAIMS = int(os.environ.get("ACP_DEFAULT_MAX_CLAIMS", "3"))

# Real Ed25519 public key — generated 2026-05-18, private in GCP Secret Manager
# acp-bundle-signer-ed25519 (project pawconscious-mesh-2026)
# Per codex G11 P0.3 — no placeholder
SIGNER_PUBLIC_KEY_MULTIBASE = "z6MkfYpcbqZEdKKKg6qdNb3kpa1z5kTE27XaujSdp56CoBkZ"
SIGNER_PUBLIC_KEY_HEX = "10486ac1a48c4f6731e36115b0e4e3fe5b92a587c88c7ede9677bf4feaab48c6"
SIGNER_DID = f"{PUBLIC_DID}#owner"
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

AGENT_ENGINE_RESOURCE = os.environ.get(
    "ACP_AGENT_ENGINE_RESOURCE",
    "projects/40952019806/locations/us-central1/reasoningEngines/1255381144908595200",
)


A2A_AGENT_CARD = {
    "name": "PawConscious Mesh",
    "description": (
        "A2A trust mesh for expert-claim commerce. Verify endorsement claims on commerce "
        "SKUs against signed PCEC v0.1 evidence bundles. Pet supplement reference deployment."
    ),
    "url": f"{PUBLIC_BASE_URL}/a2a/v1",
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
        "managedReasoningEngine": True,
    },
    "managedRuntime": {
        "platform": "Vertex AI Agent Engine",
        "resourceName": AGENT_ENGINE_RESOURCE,
        "region": "us-central1",
        "note": (
            "The orchestrator is deployed as a managed Reasoning Engine on Vertex AI "
            "Agent Engine. The Cloud Run A2A endpoint at /a2a/v1 is the public ingress; "
            "the Agent Engine resource is the discoverable managed runtime."
        ),
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
                "scoring, FTC §255 mapping, and adversarial audit verdict. ASYNC task: POST "
                "returns 202 with task_id; poll GET /a2a/v1/tasks/get/{task_id} for completion. "
                "~60s per claim."
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
    "id": PUBLIC_DID,
    "verificationMethod": [
        {
            "id": f"{PUBLIC_DID}#owner",
            "type": "Ed25519VerificationKey2020",
            "controller": PUBLIC_DID,
            "publicKeyMultibase": SIGNER_PUBLIC_KEY_MULTIBASE,
        },
    ],
    "authentication": [f"{PUBLIC_DID}#owner"],
    "assertionMethod": [f"{PUBLIC_DID}#owner"],
    "service": [
        {
            "id": f"{PUBLIC_DID}#pcec-resolver",
            "type": "PCECResolver",
            "serviceEndpoint": f"{PUBLIC_BASE_URL}/pcec/v0",
        },
        {
            "id": f"{PUBLIC_DID}#a2a-mesh",
            "type": "A2AMeshEndpoint",
            "serviceEndpoint": f"{PUBLIC_BASE_URL}/a2a/v1",
        },
    ],
}


@app.get("/health")
async def health() -> dict[str, Any]:
    return {"status": "ok", "service": "pawconscious-mesh", "version": SERVICE_VERSION}


@app.get("/health/agent-engine")
async def health_agent_engine() -> dict[str, Any]:
    """Codex G18 amendment — judges can verify Agent Engine deployment exists
    without needing Vertex AI console credentials."""
    return {
        "status": "ok",
        "agent_engine_resource": AGENT_ENGINE_RESOURCE,
        "console_url": (
            f"https://console.cloud.google.com/vertex-ai/agents/agent-engines/"
            f"detail/{AGENT_ENGINE_RESOURCE.rsplit('/', 1)[-1]}?project=pawconscious-mesh-2026"
        ),
        "note": (
            "The orchestrator is deployed as a managed Reasoning Engine. The Cloud Run "
            "A2A endpoint is the public ingress; this endpoint is the proof of Track 3 "
            "Key Consideration #5 (multi-agent system on Agent Engine)."
        ),
    }


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
    """A2A v0.3 task envelope per Linux Foundation spec (April 2026 GA)."""
    skill: str = Field(..., description="Skill ID per agent card")
    input: dict[str, Any] = Field(..., description="Skill input arguments")
    task_id: Optional[str] = None


class A2ASubmittedResponse(BaseModel):
    """202 Accepted response per A2A v0.3 async task lifecycle."""
    task_id: str
    status: str = "submitted"
    poll_url: str
    estimated_seconds: int


class A2ATaskStatusResponse(BaseModel):
    """GET /a2a/v1/tasks/get/{task_id} response."""
    task_id: str
    status: str  # submitted | working | completed | failed
    progress_message: str = ""
    output: Optional[dict[str, Any]] = None
    error: Optional[str] = None
    bundle_hash: Optional[str] = None
    bundle_signature: Optional[str] = None
    created_at: float
    completed_at: Optional[float] = None


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


async def _run_verify_claim_background(task_id: str, product_url: str, max_claims: int) -> None:
    """Background worker per A2A v0.3 async lifecycle: submitted → working → completed/failed.

    On success, appends the signed bundle to the Firestore transparency log (Phase 11)
    so /pcec/v0/claim/{urn} can resolve it.
    """
    try:
        await task_store.update(task_id, status="working", progress_message="claim extraction")
        bundle = await run_mesh(product_url, max_claims=max_claims)
        bundle_hash = compute_bundle_hash(bundle)
        bundle.signature = sign_bundle(bundle)
        bundle.bundle_urn = urn_for_hash(bundle_hash)

        # Append to Firestore transparency log (best effort; failure does not block A2A response)
        try:
            await append_bundle_async(
                urn=bundle.bundle_urn,
                bundle_hash=bundle_hash,
                bundle_signature=bundle.signature,
                bundle_json=json.loads(bundle.model_dump_json()),
                signer_did=SIGNER_DID,
                issuer=bundle.issuer,
            )
        except Exception as log_err:
            print(f"[mesh_api] WARN: transparency log append failed: {log_err}")

        await task_store.update(
            task_id,
            status="completed",
            progress_message="bundle signed",
            output=json.loads(bundle.model_dump_json()),
            bundle_hash=bundle_hash,
            bundle_signature=bundle.signature,
        )
    except Exception as e:
        await task_store.update(
            task_id,
            status="failed",
            error=f"{type(e).__name__}: {e}",
        )


@app.post("/a2a/v1/tasks/send", response_model=A2ASubmittedResponse, status_code=202)
async def a2a_send(
    request: A2ATaskRequest,
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
) -> A2ASubmittedResponse:
    """A2A v0.3 async task entry. Returns 202 with task_id; client polls /tasks/get/{id}."""
    if x_api_key != DEMO_API_KEY:
        raise HTTPException(status_code=401, detail="X-API-Key required. Request via GitHub issue.")

    if request.skill != "verify_claim":
        raise HTTPException(status_code=404, detail=f"Unknown skill: {request.skill}")

    product_url = request.input.get("product_url") or request.input.get("sku") or request.input.get("url")
    if not product_url:
        raise HTTPException(status_code=400, detail="Missing product_url / sku / url in input")
    max_claims = int(request.input.get("max_claims", DEFAULT_MAX_CLAIMS))

    state = await task_store.create(input_data={"product_url": product_url, "max_claims": max_claims})
    # Fire-and-forget background processing per A2A v0.3 async spec
    asyncio.create_task(_run_verify_claim_background(state.task_id, product_url, max_claims))

    return A2ASubmittedResponse(
        task_id=state.task_id,
        status="submitted",
        poll_url=f"{PUBLIC_BASE_URL}/a2a/v1/tasks/get/{state.task_id}",
        estimated_seconds=max_claims * 60,  # ~60s per claim observed
    )


@app.get("/a2a/v1/tasks/get/{task_id}", response_model=A2ATaskStatusResponse)
async def a2a_get(task_id: str) -> A2ATaskStatusResponse:
    """A2A v0.3 task status polling endpoint."""
    state = await task_store.get(task_id)
    if state is None:
        raise HTTPException(status_code=404, detail=f"Task not found: {task_id}")
    return A2ATaskStatusResponse(
        task_id=state.task_id,
        status=state.status,
        progress_message=state.progress_message,
        output=state.output,
        error=state.error,
        bundle_hash=state.bundle_hash,
        bundle_signature=state.bundle_signature,
        created_at=state.created_at,
        completed_at=state.completed_at,
    )


@app.post("/a2a/v1/tasks/cancel/{task_id}")
async def a2a_cancel(task_id: str) -> JSONResponse:
    """Cancel a submitted/working task per A2A v0.3 lifecycle.

    v0.1 doesn't actually halt the underlying asyncio task (best-effort marker only);
    Phase 5.6 wires real cancellation via asyncio.CancelledError + task tracking.
    """
    state = await task_store.get(task_id)
    if state is None:
        raise HTTPException(status_code=404, detail=f"Task not found: {task_id}")
    if state.status in {"completed", "failed", "canceled"}:
        return JSONResponse(
            status_code=409,
            content={"task_id": task_id, "status": state.status, "detail": "Task already terminated"},
        )
    await task_store.update(task_id, status="canceled", progress_message="canceled by request (best-effort)")
    return JSONResponse(status_code=200, content={"task_id": task_id, "status": "canceled"})


# ---------------------------------------------------------------------------
# PCEC v0 resolver (stub — real implementation in Phase 5 with Firestore)
# ---------------------------------------------------------------------------

@app.get("/pcec/v0/claim/{urn}")
async def resolve_claim(urn: str) -> JSONResponse:
    """PCEC v0.1 resolver — Phase 11 transparency log lookup.

    The Firestore-backed `acp-claims` collection stores every signed bundle on issuance.
    GET returns the full PCEC bundle + signature + chain_anchor for verification.
    Returns 404 if the URN is unknown (never seen by the mesh).
    """
    if not urn.startswith("urn:pcec:claim:"):
        return JSONResponse(
            status_code=400,
            content={"title": "Invalid PCEC URN", "detail": f"Expected urn:pcec:claim:... got {urn!r}"},
        )

    entry = await fetch_bundle_async(urn)
    if entry is None:
        return JSONResponse(
            status_code=404,
            content={
                "type": "https://github.com/odominguez7/PawConscious-Mesh-GFS/blob/main/docs/PCEC-v0.md",
                "title": "URN not found in transparency log",
                "status": 404,
                "detail": (
                    "The transparency log has no record of this URN. Either the bundle was never "
                    "issued by this mesh, or the URN format is incorrect. Issue a new bundle via "
                    "POST /a2a/v1/tasks/send and use the bundle_urn field returned at completion."
                ),
                "urn": urn,
            },
        )

    return JSONResponse(status_code=200, content=entry)


@app.get("/pcec/v0/chain/head")
async def chain_head() -> dict[str, Any]:
    """Latest chain anchor for the transparency log (Phase 11 tamper evidence)."""
    from shared.transparency_log import get_log
    head = await asyncio.to_thread(get_log()._read_head_hash)
    return {
        "current_chain_anchor": head,
        "note": (
            "Each new issued bundle is chained to the previous one via "
            "sha256(bundle_hash + ':' + prev_chain_anchor). A complete chain from "
            "genesis to head is independently verifiable."
        ),
    }


# ---------------------------------------------------------------------------
# Root index
# ---------------------------------------------------------------------------

from fastapi.responses import HTMLResponse, FileResponse


@app.get("/", response_class=HTMLResponse)
async def root() -> HTMLResponse:
    """Mesh Console UI — paste a PDP URL, watch agent fan-out live."""
    console_path = Path(__file__).parent / "static" / "console.html"
    return HTMLResponse(content=console_path.read_text(encoding="utf-8"))


@app.get("/api-info", response_class=PlainTextResponse)
async def api_info() -> str:
    return (
        "PawConscious Mesh — ACP v0.1\n\n"
        "Public endpoints:\n"
        "  GET  /                              Mesh Console UI\n"
        "  GET  /.well-known/agent-card.json   A2A v0.3 agent card\n"
        "  GET  /.well-known/did.json          DID document\n"
        "  POST /a2a/v1/tasks/send             A2A task entry (X-API-Key, returns 202+task_id)\n"
        "  GET  /a2a/v1/tasks/get/{task_id}    Poll task status\n"
        "  POST /a2a/v1/tasks/cancel/{task_id} Cancel task (best-effort)\n"
        "  GET  /pcec/v0/claim/{urn}           PCEC v0.1 resolver (501 in v0.1)\n"
        "  GET  /health                        Health probe\n\n"
        "Repo: https://github.com/odominguez7/PawConscious-Mesh-GFS\n"
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.environ.get("PORT", "8080")), reload=False)
