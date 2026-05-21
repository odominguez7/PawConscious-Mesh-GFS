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
import time
from collections import deque
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
    append_bundle_async, fetch_bundle_async, get_head_anchor_async, urn_for_hash,
)

# G19 #6 amendment: idempotency cache for /a2a/v1/tasks/send.
# Maps Idempotency-Key -> task_id so client retries return the same task.
# In-process for v0.1 (Cloud Run min=max=1); Phase 5.6 promotes to Firestore.
_idempotency_cache: dict[str, str] = {}
_idempotency_lock = asyncio.Lock()


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

# Mount /assets/* for deck-aligned imagery used by console-v2.html (Stage 2A).
from fastapi.staticfiles import StaticFiles
_assets_dir = Path(__file__).parent / "static" / "assets"
if _assets_dir.exists():
    app.mount("/assets", StaticFiles(directory=str(_assets_dir)), name="assets")


# ---------------------------------------------------------------------------
# Public well-known endpoints
# ---------------------------------------------------------------------------

AGENT_ENGINE_RESOURCE = os.environ.get(
    "ACP_AGENT_ENGINE_RESOURCE",
    "projects/40952019806/locations/us-central1/reasoningEngines/1255381144908595200",
)

# ---------------------------------------------------------------------------
# R2 — Agent Engine routing with feature flag + p95 auto-fallback
# ---------------------------------------------------------------------------
# Inline asyncio fan-out stays primary. Agent Engine is the documented Track 3
# path (managed Reasoning Engine). When ACP_USE_AGENT_ENGINE=true, verify_claim
# is routed through the deployed Reasoning Engine. If Agent Engine p95 exceeds
# `gate multiplier` * inline p95 over a rolling window, the gate auto-closes and
# subsequent requests fall back to inline. Three consecutive Agent Engine
# failures also close the gate. State is observable via /health/agent-engine-traffic.

_ACP_USE_AGENT_ENGINE_DEFAULT = os.environ.get("ACP_USE_AGENT_ENGINE", "false").lower() == "true"
_ACP_AGENT_ENGINE_P95_GATE = float(os.environ.get("ACP_AGENT_ENGINE_P95_GATE", "2.0"))
_ACP_AGENT_ENGINE_MIN_SAMPLES = int(os.environ.get("ACP_AGENT_ENGINE_MIN_SAMPLES", "5"))
_ACP_LATENCY_WINDOW_SIZE = int(os.environ.get("ACP_LATENCY_WINDOW_SIZE", "20"))
_AGENT_ENGINE_CONSEC_FAIL_LIMIT = 3
# Codex Day-19 P2 amendment: when flag starts ON, no inline samples ever accrue
# so the p95 gate can only close via consecutive failures. Set a documented
# baseline (ms) and the gate falls back to it when the live inline window is empty.
# Default 90000ms (90s) matches observed inline p95 from L1 eval; override per env.
_ACP_INLINE_P95_BASELINE_MS = float(os.environ.get("ACP_INLINE_P95_BASELINE_MS", "90000"))
# Codex Day-19 amend pass: hung engine.query() leaves the task stuck in `working`,
# no latency sample lands, and the p95 gate can never close → no fallback to inline.
# Hard upper bound per request. Default 180s = 3x typical p95 observed in L1 eval.
# Treat asyncio.TimeoutError as a failure: records latency = timeout value, falls
# through to inline path, increments consec_failures so 3 hangs in a row close the gate.
_ACP_AGENT_ENGINE_QUERY_TIMEOUT_S = float(os.environ.get("ACP_AGENT_ENGINE_QUERY_TIMEOUT_S", "180"))

_latency_inline_ms: deque[float] = deque(maxlen=_ACP_LATENCY_WINDOW_SIZE)
_latency_agent_engine_ms: deque[float] = deque(maxlen=_ACP_LATENCY_WINDOW_SIZE)
_traffic_gate_open: bool = _ACP_USE_AGENT_ENGINE_DEFAULT
_traffic_gate_reason: str = (
    "initial: feature flag ON" if _ACP_USE_AGENT_ENGINE_DEFAULT
    else "initial: feature flag OFF (inline asyncio is the only path)"
)
_agent_engine_consec_failures: int = 0
_traffic_gate_lock = asyncio.Lock()
_agent_engine_client_cache: Any = None


def _percentile(samples: list[float], pct: float) -> Optional[float]:
    if not samples:
        return None
    ordered = sorted(samples)
    idx = int(len(ordered) * pct)
    return ordered[max(0, min(idx, len(ordered) - 1))]


def _agent_engine_region() -> tuple[str, str]:
    # projects/<num>/locations/<loc>/reasoningEngines/<id>
    parts = AGENT_ENGINE_RESOURCE.split("/")
    return parts[1], parts[3]


def _get_agent_engine_client():
    """Lazy + cached Reasoning Engine client. First call pays vertexai.init().
    Subsequent calls return the cached engine handle."""
    global _agent_engine_client_cache
    if _agent_engine_client_cache is None:
        import vertexai  # type: ignore
        from vertexai import agent_engines  # type: ignore
        project_id, location = _agent_engine_region()
        vertexai.init(project=project_id, location=location)
        _agent_engine_client_cache = agent_engines.get(AGENT_ENGINE_RESOURCE)
    return _agent_engine_client_cache


async def _route_verify_path() -> str:
    """Returns 'agent_engine' or 'inline'. Single read under the gate lock so
    routing is consistent with whatever the gate just decided."""
    async with _traffic_gate_lock:
        return "agent_engine" if _traffic_gate_open else "inline"


async def _record_latency(path: str, latency_ms: float, succeeded: bool) -> None:
    """Update the per-path latency window and re-evaluate the gate."""
    global _traffic_gate_open, _traffic_gate_reason, _agent_engine_consec_failures
    async with _traffic_gate_lock:
        if path == "agent_engine":
            if succeeded:
                _latency_agent_engine_ms.append(latency_ms)
                _agent_engine_consec_failures = 0
            else:
                _agent_engine_consec_failures += 1
                if (
                    _agent_engine_consec_failures >= _AGENT_ENGINE_CONSEC_FAIL_LIMIT
                    and _traffic_gate_open
                ):
                    _traffic_gate_open = False
                    _traffic_gate_reason = (
                        f"agent-engine failed {_AGENT_ENGINE_CONSEC_FAIL_LIMIT} consecutive "
                        f"times; flipped to inline"
                    )
                return
        elif path == "inline" and succeeded:
            _latency_inline_ms.append(latency_ms)

        if not _traffic_gate_open:
            return
        if len(_latency_agent_engine_ms) >= _ACP_AGENT_ENGINE_MIN_SAMPLES:
            p95_ae = _percentile(list(_latency_agent_engine_ms), 0.95)
            if len(_latency_inline_ms) >= _ACP_AGENT_ENGINE_MIN_SAMPLES:
                p95_inline = _percentile(list(_latency_inline_ms), 0.95)
                inline_source = "live"
            else:
                p95_inline = _ACP_INLINE_P95_BASELINE_MS
                inline_source = "baseline"
            if p95_ae and p95_inline and p95_ae > _ACP_AGENT_ENGINE_P95_GATE * p95_inline:
                _traffic_gate_open = False
                _traffic_gate_reason = (
                    f"agent-engine p95={p95_ae:.0f}ms > "
                    f"{_ACP_AGENT_ENGINE_P95_GATE}x inline p95={p95_inline:.0f}ms "
                    f"({inline_source}); flipped to inline"
                )


async def _run_mesh_via_agent_engine(product_url: str, max_claims: int) -> EndorsementClaimBundle:
    """Invoke deployed Reasoning Engine.query() in a worker thread (sync API),
    rebuild EndorsementClaimBundle from the returned JSON so the caller can
    hash + sign + log identically to the inline path.

    Codex Day-19 amend pass: wrap the query in asyncio.wait_for so a stalled
    Vertex AI backend can't strand the background task in `working` indefinitely.
    On timeout, asyncio.TimeoutError raises out and the caller's existing
    `except Exception` records the failure + falls through to inline.
    """
    engine = await asyncio.to_thread(_get_agent_engine_client)
    bundle_json = await asyncio.wait_for(
        asyncio.to_thread(engine.query, product_url, max_claims),
        timeout=_ACP_AGENT_ENGINE_QUERY_TIMEOUT_S,
    )
    return EndorsementClaimBundle(**bundle_json)


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
            "GFS JUDGES — demo key: `demo-key-2026-06`. Add header "
            "`X-API-Key: demo-key-2026-06` to any /a2a/v1/* request. "
            "Public open access ships post-hackathon once abuse controls validated."
        ),
    },
    "envelopes": {
        "accepted": ["a2a-v0.3", "pawconscious-flat-v0.1"],
        "examples": {
            "a2a-v0.3": {
                "message": {
                    "role": "user",
                    "parts": [{"type": "text", "text": "https://www.nativepet.com/products/hip-joint"}],
                },
                "skill": "verify_claim",
            },
            "pawconscious-flat-v0.1": {
                "skill": "verify_claim",
                "input": {"product_url": "https://www.nativepet.com/products/hip-joint"},
            },
        },
        "note": (
            "POST /a2a/v1/tasks/send accepts BOTH the Linux Foundation A2A v0.3 standard "
            "envelope (message.parts[].text containing the product URL) AND a flat "
            "{skill, input} shape. Standards-compliant A2A clients can call this endpoint "
            "without translation. JSON-RPC 2.0 wrapping (params.message) is also accepted."
        ),
    },
    "defaultInputModes": ["text", "application/json"],
    "defaultOutputModes": ["application/ld+json", "text"],
    "skills": [
        {
            "id": "verify_claim",
            "name": "Verify endorsement claim",
            "description": (
                "Given a product URL, run the full mesh pipeline (7 specialized agents on "
                "Google Cloud: 1 ADK + 6 google.genai direct) and return a signed PCEC v0.1 "
                "evidence bundle with vet-rubric scoring, FTC §255 mapping, adversarial audit "
                "verdict, a branded executive cert, and an adversarial Second Opinion using "
                "Google Search grounding. ASYNC task: POST returns 202 with task_id; poll GET "
                "/a2a/v1/tasks/get/{task_id} for completion. ~30-45s per claim."
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
    without needing Vertex AI console credentials.

    R2 update: also surfaces traffic gate state so judges can see whether the
    Reasoning Engine is in the live verify_claim path or shadow-only.
    """
    async with _traffic_gate_lock:
        gate_open = _traffic_gate_open
        gate_reason = _traffic_gate_reason
    return {
        "status": "ok",
        "agent_engine_resource": AGENT_ENGINE_RESOURCE,
        "console_url": (
            f"https://console.cloud.google.com/vertex-ai/agents/agent-engines/"
            f"detail/{AGENT_ENGINE_RESOURCE.rsplit('/', 1)[-1]}?project=pawconscious-mesh-2026"
        ),
        "feature_flag_use_agent_engine": _ACP_USE_AGENT_ENGINE_DEFAULT,
        "traffic_gate_open": gate_open,
        "traffic_gate_reason": gate_reason,
        "traffic_detail_url": f"{PUBLIC_BASE_URL}/health/agent-engine-traffic",
        "note": (
            "The orchestrator is deployed as a managed Reasoning Engine. The Cloud Run "
            "A2A endpoint is the public ingress; this endpoint is the proof of Track 3 "
            "Key Consideration #5 (multi-agent system on Agent Engine). When the feature "
            "flag is ON and the p95 gate is OPEN, verify_claim is routed through the "
            "Reasoning Engine; otherwise it runs inline."
        ),
    }


@app.get("/health/agent-engine-traffic")
async def health_agent_engine_traffic() -> dict[str, Any]:
    """R2 — observable traffic gate state. Judges + operators can see whether the
    Agent Engine path is currently carrying traffic and why."""
    async with _traffic_gate_lock:
        gate_open = _traffic_gate_open
        gate_reason = _traffic_gate_reason
        consec_failures = _agent_engine_consec_failures
        inline_samples = list(_latency_inline_ms)
        ae_samples = list(_latency_agent_engine_ms)
    p95_inline = _percentile(inline_samples, 0.95)
    p95_ae = _percentile(ae_samples, 0.95)
    inline_p95_source = "live" if len(inline_samples) >= _ACP_AGENT_ENGINE_MIN_SAMPLES else "baseline"
    inline_p95_for_gate = (
        p95_inline if inline_p95_source == "live" else _ACP_INLINE_P95_BASELINE_MS
    )
    return {
        "feature_flag_use_agent_engine": _ACP_USE_AGENT_ENGINE_DEFAULT,
        "traffic_gate_open": gate_open,
        "traffic_gate_reason": gate_reason,
        "gate_multiplier": _ACP_AGENT_ENGINE_P95_GATE,
        "min_samples_to_gate": _ACP_AGENT_ENGINE_MIN_SAMPLES,
        "window_size": _ACP_LATENCY_WINDOW_SIZE,
        "agent_engine_p95_ms": p95_ae,
        "inline_p95_ms": p95_inline,
        "inline_p95_baseline_ms": _ACP_INLINE_P95_BASELINE_MS,
        "inline_p95_source_for_gate": inline_p95_source,
        "inline_p95_used_for_gate_ms": inline_p95_for_gate,
        "agent_engine_samples": len(ae_samples),
        "inline_samples": len(inline_samples),
        "agent_engine_consecutive_failures": consec_failures,
        "consecutive_failure_limit": _AGENT_ENGINE_CONSEC_FAIL_LIMIT,
        "query_timeout_s": _ACP_AGENT_ENGINE_QUERY_TIMEOUT_S,
        "note": (
            "R2: traffic to Agent Engine is feature-flagged + p95-gated. Inline asyncio "
            "stays primary; Agent Engine is the documented Track 3 path. If Agent Engine "
            "p95 exceeds the gate multiplier × inline p95 over the rolling window, the "
            "gate auto-closes and subsequent requests fall back to inline. Three consecutive "
            "Agent Engine failures also close the gate. Each engine.query() call has a "
            "hard timeout (ACP_AGENT_ENGINE_QUERY_TIMEOUT_S, default 180s); a timeout is "
            "treated as a failure so the gate logic + fallback path still fire. Codex "
            "Day-19 P2: when the flag starts ON and no live inline samples exist, the "
            "gate compares against ACP_INLINE_P95_BASELINE_MS instead so the latency gate still fires."
        ),
    }


@app.get("/health/vertex-search")
async def health_vertex_search() -> dict[str, Any]:
    """R1 probe — judges can verify the Vertex AI Search corpus exists and is
    indexed without needing Vertex AI console credentials.

    Returns the data store path, sources count, and a sample retrieval against
    a canonical claim. If the corpus is missing or empty, this endpoint surfaces
    that fact rather than silently swallowing the failure (per N3 amendment).
    """
    try:
        from agents.compliance import (
            VERTEX_SEARCH_PROJECT,
            VERTEX_SEARCH_LOCATION,
            VERTEX_SEARCH_DATA_STORE,
            retrieve_grounding_sources,
        )
        from shared.pcec_schema import Claim, ClaimKind
        probe_claim = Claim(
            text="endorsement substantiation evidence",
            kind=ClaimKind.EFFICACY,
        )
        sources = await retrieve_grounding_sources(probe_claim, max_results=3)
        sample = [
            {"source_id": s.source_id, "snippet_hash": s.snippet_hash}
            for s in sources[:3]
        ]
        status = "ok" if sources else "empty"
        data_store_path = (
            f"projects/{VERTEX_SEARCH_PROJECT}/locations/{VERTEX_SEARCH_LOCATION}/"
            f"collections/default_collection/dataStores/{VERTEX_SEARCH_DATA_STORE}"
        )
        probe_text = probe_claim.text
        sources_count = len(sources)
    except Exception as e:
        return {
            "status": f"error:{type(e).__name__}",
            "error_detail": str(e)[:300],
            "note": "Live probe failed at startup. Compliance agent will run prompt-only.",
        }
    return {
        "status": status,
        "data_store": data_store_path,
        "probe_query": probe_text,
        "sources_returned": sources_count,
        "sample": sample,
        "note": (
            "Live probe against the FTC §255 + AAFCO PF7 + NASC corpus. "
            "If status != 'ok', the compliance agent will run prompt-only — "
            "surfacing the failure mode instead of silently falling back."
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

class A2APart(BaseModel):
    """A2A v0.3 message part — one element of a multi-modal message."""
    type: str = Field("text", description="Part type: text | json | binary")
    text: Optional[str] = None
    data: Optional[dict[str, Any]] = None


class A2AMessage(BaseModel):
    """A2A v0.3 message — role + parts list, multi-modal."""
    role: str = Field("user", description="Message role: user | agent")
    parts: list[A2APart] = Field(default_factory=list)


class A2ATaskRequest(BaseModel):
    """A2A v0.3 task envelope — dual-shape acceptance (B4 amendment 2026-05-21).

    Accepts BOTH:
    - Flat shape (PawConscious proprietary, also documented in agent card):
        {"skill": "verify_claim", "input": {"product_url": "..."}}
    - A2A v0.3 standard envelope (Linux Foundation spec, April 2026 GA):
        {"message": {"role":"user", "parts":[{"type":"text", "text":"<url>"}]},
         "skill": "verify_claim"  // optional; defaults to verify_claim
        }
      The standard envelope can wrap in JSON-RPC 2.0 (`params: {message: ...}`) too.

    Field resolution order for the product URL:
      1. input.product_url / input.sku / input.url   (flat shape)
      2. params.message.parts[*].text                (JSON-RPC wrap of A2A v0.3)
      3. message.parts[*].text                       (bare A2A v0.3)

    The agent card declares dual support; judges running standards-compliant A2A
    clients can call this endpoint without translation.
    """
    skill: Optional[str] = Field(None, description="Skill ID per agent card (default: verify_claim)")
    input: Optional[dict[str, Any]] = Field(None, description="Flat skill input arguments")
    message: Optional[A2AMessage] = Field(None, description="A2A v0.3 standard message envelope")
    params: Optional[dict[str, Any]] = Field(None, description="JSON-RPC 2.0 params (wraps `message`)")
    task_id: Optional[str] = None
    # JSON-RPC envelope fields — accepted and ignored. Present so strict A2A clients
    # don't see unexpected-field warnings.
    jsonrpc: Optional[str] = None
    method: Optional[str] = None
    id: Optional[str] = None

    def resolve_url_and_skill(self) -> tuple[Optional[str], str, dict[str, Any]]:
        """Extract (product_url_or_urn, skill, raw_input_for_replay) from any accepted shape.

        For skill=verify_claim: returns the product URL.
        For skill=fetch_substantiation_bundle: returns the PCEC URN as the
        positional value, so a2a_send can route it to the resolver.
        """
        # Resolve message: direct, or via JSON-RPC params wrapper
        msg = self.message
        if msg is None and self.params and isinstance(self.params, dict):
            params_msg = self.params.get("message")
            if isinstance(params_msg, dict):
                try:
                    msg = A2AMessage(**params_msg)
                except Exception:
                    msg = None
        # Resolve skill: explicit, then params.skill, then default
        skill = self.skill
        if not skill and self.params and isinstance(self.params, dict):
            skill = self.params.get("skill")
        if not skill:
            skill = "verify_claim"
        # Resolve URL or URN — flat input wins; fall back to parts[*] extraction.
        # For fetch_substantiation_bundle the "url" slot carries the URN.
        # Codex Day 18 P1: URN-shaped values are only accepted when the resolved
        # skill is fetch_substantiation_bundle; for verify_claim we require a real
        # URL so a misrouted URN cannot reach the downstream fetcher.
        url = None
        text_fallback: Optional[str] = None
        replay_input: dict[str, Any] = {}
        is_fetch_bundle = (skill == "fetch_substantiation_bundle")

        def _accept_token(tok: Optional[str]) -> Optional[str]:
            """Return the token if it matches the active skill's expected shape."""
            if not tok:
                return None
            if is_fetch_bundle:
                return tok if tok.startswith("urn:pcec:claim:") else None
            return tok if (tok.startswith("http://") or tok.startswith("https://")) else None

        if self.input:
            replay_input = dict(self.input)
            if is_fetch_bundle:
                url = _accept_token(self.input.get("urn") or self.input.get("bundle_urn"))
            else:
                url = _accept_token(
                    self.input.get("product_url")
                    or self.input.get("sku")
                    or self.input.get("url")
                )
        if not url and msg:
            for p in msg.parts:
                if url:
                    break
                if p.type == "text" and p.text:
                    candidate = p.text.strip()
                    accepted = _accept_token(candidate)
                    if accepted:
                        url = accepted
                    elif text_fallback is None:
                        text_fallback = candidate
                elif p.type == "json" and isinstance(p.data, dict):
                    replay_input.update(p.data)
                    if is_fetch_bundle:
                        url = _accept_token(p.data.get("urn") or p.data.get("bundle_urn"))
                    else:
                        url = _accept_token(
                            p.data.get("product_url")
                            or p.data.get("url")
                            or p.data.get("sku")
                        )
            if not url:
                # Second pass to absorb later json parts even after a text fallback.
                for p in msg.parts:
                    if p.type == "json" and isinstance(p.data, dict):
                        replay_input.update(p.data)
                        if is_fetch_bundle:
                            url = _accept_token(p.data.get("urn") or p.data.get("bundle_urn"))
                        else:
                            url = _accept_token(
                                p.data.get("product_url")
                                or p.data.get("url")
                                or p.data.get("sku")
                            )
                        if url:
                            break
            # Only accept the text fallback if it matches the active skill's shape.
            if not url and text_fallback and _accept_token(text_fallback):
                url = text_fallback
        if url and not is_fetch_bundle and "product_url" not in replay_input:
            replay_input["product_url"] = url
        return url, skill, replay_input


class A2ASubmittedResponse(BaseModel):
    """202 Accepted response per A2A v0.3 async task lifecycle.

    G19 #4 amendment: include head_anchor_at_submit so the client can later
    verify chain continuity without a second round trip.
    """
    task_id: str
    status: str = "submitted"
    poll_url: str
    estimated_seconds: int
    head_anchor_at_submit: Optional[str] = None
    idempotency_key: Optional[str] = None
    idempotent_replay: bool = False


class A2ATaskStatusResponse(BaseModel):
    """GET /a2a/v1/tasks/get/{task_id} response."""
    task_id: str
    status: str  # submitted | working | completed | failed
    progress_message: str = ""
    output: Optional[dict[str, Any]] = None
    error: Optional[str] = None
    bundle_hash: Optional[str] = None
    bundle_signature: Optional[str] = None
    chain_anchor: Optional[str] = None
    # v0.8.0 — outputs from Agent 6 (Cert Composer) + Agent 7 (Second Opinion).
    # Both are post-merge and don't block the signed bundle if they fail.
    cert_html: Optional[str] = None
    second_opinion: Optional[dict[str, Any]] = None
    created_at: float
    completed_at: Optional[float] = None


# Pydantic v2 forward-ref resolution. `from __future__ import annotations`
# stringifies every annotation, so nested model refs (A2AMessage, A2APart)
# must be rebuilt with the local namespace once all referenced classes exist.
A2APart.model_rebuild()
A2AMessage.model_rebuild()
A2ATaskRequest.model_rebuild()
A2ASubmittedResponse.model_rebuild()
A2ATaskStatusResponse.model_rebuild()


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

    R2: when ACP_USE_AGENT_ENGINE=true AND the p95 gate is open, the mesh runs via
    the deployed Vertex AI Reasoning Engine. Otherwise it runs inline (asyncio fan-out).
    Latency per path is recorded; if Agent Engine p95 > N x inline p95, gate auto-closes.
    """
    try:
        path = await _route_verify_path()
        await task_store.update(
            task_id,
            status="working",
            progress_message=f"claim extraction (path={path})",
        )
        t0 = time.perf_counter()
        if path == "agent_engine":
            try:
                bundle = await _run_mesh_via_agent_engine(product_url, max_claims=max_claims)
            except Exception as ae_err:
                latency_ms = (time.perf_counter() - t0) * 1000.0
                await _record_latency("agent_engine", latency_ms, succeeded=False)
                print(f"[mesh_api] WARN: agent-engine path failed: {ae_err}; falling back to inline")
                await task_store.update(
                    task_id,
                    progress_message=f"agent-engine path failed ({type(ae_err).__name__}); falling back to inline",
                )
                t0 = time.perf_counter()
                path = "inline"
                bundle = await run_mesh(product_url, max_claims=max_claims)
        else:
            bundle = await run_mesh(product_url, max_claims=max_claims)
        latency_ms = (time.perf_counter() - t0) * 1000.0
        await _record_latency(path, latency_ms, succeeded=True)
        bundle_hash = compute_bundle_hash(bundle)
        bundle.signature = sign_bundle(bundle)
        bundle.bundle_urn = urn_for_hash(bundle_hash)

        # Append to Firestore transparency log (best effort; failure does not block A2A response)
        # G20 P1: capture chain_anchor from the log entry so the certificate can
        # display the real chain anchor (not bundle_hash) as judge-visible proof.
        chain_anchor: Optional[str] = None
        try:
            log_entry = await append_bundle_async(
                urn=bundle.bundle_urn,
                bundle_hash=bundle_hash,
                bundle_signature=bundle.signature,
                bundle_json=json.loads(bundle.model_dump_json()),
                signer_did=SIGNER_DID,
                issuer=bundle.issuer,
            )
            chain_anchor = log_entry.get("chain_anchor") if isinstance(log_entry, dict) else None
        except Exception as log_err:
            print(f"[mesh_api] WARN: transparency log append failed: {log_err}")

        # Mark the bundle stage complete BEFORE the cert + second-opinion agents
        # run, so the frontend sees the verify finish and immediately starts
        # rendering. Cert + second-opinion attach incrementally below.
        await task_store.update(
            task_id,
            status="completed",
            progress_message="bundle signed · composing cert",
            output=json.loads(bundle.model_dump_json()),
            bundle_hash=bundle_hash,
            bundle_signature=bundle.signature,
            chain_anchor=chain_anchor,
        )

        # AGENT 6 — Cert Composer. Best-effort: if Gemini fails, frontend falls back
        # to its static cert template so verify is never blocked by composition.
        try:
            from agents.report_writer import compose_cert
            cert_html = await compose_cert(bundle, bundle_hash, chain_anchor)
            await task_store.update(task_id, cert_html=cert_html, progress_message="cert composed · running second opinion")
        except Exception as cert_err:
            print(f"[mesh_api] WARN: cert composer failed: {cert_err}")

        # AGENT 7 — Second Opinion. Adversarial double-validation via Google Search
        # grounding. Best-effort: if it fails, base bundle stands.
        try:
            from agents.second_opinion import get_second_opinion
            second_opinion = await get_second_opinion(bundle)
            await task_store.update(task_id, second_opinion=second_opinion, progress_message="second opinion delivered")
        except Exception as so_err:
            print(f"[mesh_api] WARN: second opinion failed: {so_err}")
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
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
) -> A2ASubmittedResponse:
    """A2A v0.3 async task entry. Returns 202 with task_id; client polls /tasks/get/{id}.

    G19 amendments:
    - Idempotency-Key header: client retries with the same key return the same task_id
      (prevents duplicate appends to the transparency log on transient network errors).
    - head_anchor_at_submit: current chain head returned so the client can verify the
      bundle issued by this request links to the chain it expected.
    """
    if x_api_key != DEMO_API_KEY:
        raise HTTPException(
            status_code=401,
            detail=(
                "X-API-Key required. Demo key for GFS judges: `demo-key-2026-06`. "
                "Add header `X-API-Key: demo-key-2026-06` and retry."
            ),
        )

    product_url, skill_id, resolved_input = request.resolve_url_and_skill()

    if skill_id not in ("verify_claim", "fetch_substantiation_bundle"):
        raise HTTPException(
            status_code=404,
            detail=(
                f"Unknown skill: {skill_id}. Accepted skills (per /.well-known/agent-card.json): "
                "`verify_claim` (URL in, signed bundle out), "
                "`fetch_substantiation_bundle` (PCEC URN in, full bundle out)."
            ),
        )

    # N1 — fetch_substantiation_bundle: synchronous resolve from the Firestore
    # transparency log. No background task; returns 202 with task_id that
    # immediately polls completed (consistent with the A2A async lifecycle).
    if skill_id == "fetch_substantiation_bundle":
        urn = product_url  # resolver overloads the slot; for this skill it carries the URN
        if not urn or not urn.startswith("urn:pcec:claim:"):
            raise HTTPException(
                status_code=400,
                detail=(
                    "Missing or invalid PCEC URN. Accepted shapes: "
                    "(1) flat `{\"skill\":\"fetch_substantiation_bundle\",\"input\":{\"urn\":\"urn:pcec:claim:...\"}}` or "
                    "(2) A2A v0.3 `{\"message\":{\"parts\":[{\"type\":\"text\",\"text\":\"urn:pcec:claim:...\"}]}}`. "
                    "Issue a new bundle first via skill=verify_claim and reuse the returned bundle_urn."
                ),
            )
        entry = await fetch_bundle_async(urn)
        if entry is None:
            raise HTTPException(
                status_code=404,
                detail=(
                    f"URN {urn!r} not found in transparency log. Either the bundle was never "
                    "issued by this mesh, or the URN format is incorrect. Issue a new bundle via "
                    "skill=verify_claim and reuse the returned bundle_urn."
                ),
            )
        # Synthesize a completed-task envelope so A2A clients use one polling pattern.
        state = await task_store.create(
            input_data={"urn": urn, "skill": "fetch_substantiation_bundle"}
        )
        await task_store.update(
            state.task_id,
            status="completed",
            progress_message="bundle resolved from transparency log",
            output=entry,
            bundle_hash=(entry or {}).get("bundle_hash"),
            bundle_signature=(entry or {}).get("bundle_signature"),
            chain_anchor=(entry or {}).get("chain_anchor"),
        )
        head_anchor = await get_head_anchor_async()
        return A2ASubmittedResponse(
            task_id=state.task_id,
            status="completed",
            poll_url=f"{PUBLIC_BASE_URL}/a2a/v1/tasks/get/{state.task_id}",
            estimated_seconds=0,
            head_anchor_at_submit=head_anchor,
            idempotency_key=idempotency_key,
            idempotent_replay=False,
        )

    if not product_url:
        raise HTTPException(
            status_code=400,
            detail=(
                "Missing product URL. Accepted shapes: "
                "(1) flat `{\"skill\":\"verify_claim\",\"input\":{\"product_url\":\"https://...\"}}` or "
                "(2) A2A v0.3 `{\"message\":{\"role\":\"user\",\"parts\":[{\"type\":\"text\",\"text\":\"https://...\"}]}}`."
            ),
        )
    max_claims = int(resolved_input.get("max_claims", DEFAULT_MAX_CLAIMS))

    # G19 #6: idempotency replay — same Idempotency-Key returns the same task.
    if idempotency_key:
        async with _idempotency_lock:
            existing_task_id = _idempotency_cache.get(idempotency_key)
        if existing_task_id is not None:
            existing_state = await task_store.get(existing_task_id)
            if existing_state is not None:
                head_anchor = await get_head_anchor_async()
                return A2ASubmittedResponse(
                    task_id=existing_state.task_id,
                    status=existing_state.status,
                    poll_url=f"{PUBLIC_BASE_URL}/a2a/v1/tasks/get/{existing_state.task_id}",
                    estimated_seconds=max(0, max_claims * 60),
                    head_anchor_at_submit=head_anchor,
                    idempotency_key=idempotency_key,
                    idempotent_replay=True,
                )

    state = await task_store.create(input_data={"product_url": product_url, "max_claims": max_claims})

    if idempotency_key:
        async with _idempotency_lock:
            _idempotency_cache[idempotency_key] = state.task_id

    # Fire-and-forget background processing per A2A v0.3 async spec
    asyncio.create_task(_run_verify_claim_background(state.task_id, product_url, max_claims))

    # G19 #4: return chain head at submit time
    head_anchor = await get_head_anchor_async()

    return A2ASubmittedResponse(
        task_id=state.task_id,
        status="submitted",
        poll_url=f"{PUBLIC_BASE_URL}/a2a/v1/tasks/get/{state.task_id}",
        estimated_seconds=max_claims * 60,  # ~60s per claim observed
        head_anchor_at_submit=head_anchor,
        idempotency_key=idempotency_key,
        idempotent_replay=False,
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
        chain_anchor=state.chain_anchor,
        cert_html=state.cert_html,
        second_opinion=state.second_opinion,
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
    head = await get_head_anchor_async()
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


# ---------------------------------------------------------------------------
# U1+U2 — Global nav + footer (one source of truth, included on every page)
# ---------------------------------------------------------------------------

_GLOBAL_CHROME_CSS = """
<style id="pc-global-chrome">
.pc-globalnav { position:sticky; top:0; z-index:200; background:rgba(10,11,13,0.92); backdrop-filter:saturate(140%) blur(12px); -webkit-backdrop-filter:saturate(140%) blur(12px); border-bottom:1px solid rgba(255,255,255,0.08); }
.pc-globalnav-inner { max-width:1400px; margin:0 auto; padding:14px 24px; display:flex; align-items:center; gap:24px; font-family:'JetBrains Mono', ui-monospace, monospace; }
.pc-globalnav-brand { color:#EDEEF1; text-decoration:none; font-weight:700; letter-spacing:-0.01em; font-size:15px; font-family:'Geist','Inter',system-ui,sans-serif; }
.pc-globalnav-brand .pc-globalnav-mark { color:#00D4FF; font-style:italic; font-weight:500; margin-left:2px; }
.pc-globalnav-links { display:flex; gap:2px; flex:1; margin-left:8px; }
.pc-globalnav-links a { color:rgba(237,238,241,0.62); text-decoration:none; padding:8px 14px; font-size:11px; letter-spacing:0.18em; text-transform:uppercase; border-radius:4px; transition:color 0.15s, background 0.15s; }
.pc-globalnav-links a:hover { color:#EDEEF1; background:rgba(255,255,255,0.04); text-decoration:none; }
.pc-globalnav-links a.pc-active { color:#00D4FF; background:rgba(0,212,255,0.08); }
.pc-globalnav-github { color:#00D4FF; text-decoration:none; font-size:11px; letter-spacing:0.18em; text-transform:uppercase; padding:8px 14px; border:1px solid rgba(0,212,255,0.4); border-radius:4px; font-family:'JetBrains Mono', ui-monospace, monospace; }
.pc-globalnav-github:hover { background:rgba(0,212,255,0.08); text-decoration:none; }
.pc-globalfooter { background:#0A0B0D; border-top:1px solid rgba(255,255,255,0.08); padding:48px 24px 24px; margin-top:80px; font-family:'Geist','Inter',system-ui,sans-serif; color:rgba(237,238,241,0.62); }
.pc-globalfooter-inner { max-width:1400px; margin:0 auto; display:grid; grid-template-columns:repeat(5,1fr); gap:32px; }
.pc-globalfooter-col h4 { margin:0 0 12px; font-size:11px; font-weight:700; letter-spacing:0.18em; text-transform:uppercase; color:#00D4FF; font-family:'JetBrains Mono', ui-monospace, monospace; }
.pc-globalfooter-col a, .pc-globalfooter-col span { display:block; padding:4px 0; color:rgba(237,238,241,0.62); text-decoration:none; font-size:12.5px; line-height:1.6; }
.pc-globalfooter-col a:hover { color:#00D4FF; text-decoration:none; }
.pc-globalfooter-meta { max-width:1400px; margin:32px auto 0; padding-top:20px; border-top:1px solid rgba(255,255,255,0.06); font-family:'JetBrains Mono', ui-monospace, monospace; font-size:10.5px; letter-spacing:0.14em; text-transform:uppercase; color:rgba(237,238,241,0.42); }
@media (max-width: 760px) { .pc-globalnav-inner { padding:10px 16px; gap:12px; } .pc-globalnav-links { gap:0; flex-wrap:wrap; margin-left:0; } .pc-globalnav-github { display:none; } .pc-globalfooter-inner { grid-template-columns:repeat(2,1fr); gap:24px; } }
</style>
"""

_GLOBAL_NAV_TEMPLATE = """
<header class="pc-globalnav">
  <div class="pc-globalnav-inner">
    <a class="pc-globalnav-brand" href="/">PawConscious<span class="pc-globalnav-mark">Mesh</span></a>
    <nav class="pc-globalnav-links" aria-label="Primary">
      <a href="/" data-page="product" {active_product}>Product</a>
      <a href="/agents" data-page="developers" {active_developers}>Developers</a>
      <a href="/architecture" data-page="architecture" {active_architecture}>Architecture</a>
      <a href="/demo/shopper" data-page="demo" {active_demo}>Demo</a>
    </nav>
    <a class="pc-globalnav-github" href="https://github.com/odominguez7/PawConscious-Mesh-GFS" target="_blank" rel="noopener">GitHub ↗</a>
  </div>
</header>
"""

_GLOBAL_FOOTER_HTML = """
<footer class="pc-globalfooter">
  <div class="pc-globalfooter-inner">
    <div class="pc-globalfooter-col">
      <h4>Product</h4>
      <a href="/">Overview</a>
      <a href="/demo/shopper">Live demo</a>
      <a href="/#biz">Pricing</a>
    </div>
    <div class="pc-globalfooter-col">
      <h4>Developers</h4>
      <a href="/agents">API reference</a>
      <a href="/.well-known/agent-card.json" target="_blank" rel="noopener">Agent card</a>
      <a href="/architecture">Architecture</a>
    </div>
    <div class="pc-globalfooter-col">
      <h4>Trust</h4>
      <a href="/.well-known/did.json" target="_blank" rel="noopener">DID document</a>
      <a href="/pcec/v0/chain/head" target="_blank" rel="noopener">Chain head</a>
      <a href="/health/vertex-search" target="_blank" rel="noopener">Vertex Search</a>
      <a href="/health/agent-engine" target="_blank" rel="noopener">Agent Engine</a>
    </div>
    <div class="pc-globalfooter-col">
      <h4>Company</h4>
      <a href="https://github.com/odominguez7/PawConscious-Mesh-GFS" target="_blank" rel="noopener">GitHub</a>
      <a href="/api-info" target="_blank" rel="noopener">API info</a>
    </div>
    <div class="pc-globalfooter-col">
      <h4>Legal</h4>
      <span>MIT License</span>
      <span>PCEC v0.1 spec CC-BY-4.0</span>
    </div>
  </div>
  <div class="pc-globalfooter-meta">
    PawConscious Mesh · Agentic Compliance Protocol · GFS AI Agents Challenge Track 3
  </div>
</footer>
"""


def _global_nav(active: str) -> str:
    """Render the global nav with the active page link styled.

    `active` is one of: product · developers · architecture · demo.
    """
    flags = {
        "active_product": "",
        "active_developers": "",
        "active_architecture": "",
        "active_demo": "",
    }
    key = f"active_{active}"
    if key in flags:
        flags[key] = 'class="pc-active" aria-current="page"'
    return _GLOBAL_NAV_TEMPLATE.format(**flags)


def _render_page(filename: str, active: str) -> str:
    """Read a static HTML file and inject global chrome.

    Substitutes `<!--GLOBAL_NAV-->`, `<!--GLOBAL_FOOTER-->`, and
    `<!--GLOBAL_CHROME_CSS-->` markers. If a marker is missing the
    file is returned unchanged (defensive — pages can opt out).
    """
    path = Path(__file__).parent / "static" / filename
    html = path.read_text(encoding="utf-8")
    html = html.replace("<!--GLOBAL_CHROME_CSS-->", _GLOBAL_CHROME_CSS)
    html = html.replace("<!--GLOBAL_NAV-->", _global_nav(active))
    html = html.replace("<!--GLOBAL_FOOTER-->", _GLOBAL_FOOTER_HTML)
    return html


@app.get("/", response_class=HTMLResponse)
async def root(v: Optional[str] = None) -> HTMLResponse:
    """Console UI. Default = v2 (deck-aligned redesign, flipped 2026-05-19 night after Stage 2A.x
    + v0.3.x codex handshakes cleared and E2E verified). v1 always available at /?v=v1 as fallback.
    """
    filename = "console.html" if v == "v1" else "console-v2.html"
    return HTMLResponse(content=_render_page(filename, active="product"))


@app.get("/demo/shopper", response_class=HTMLResponse)
async def shopper_demo() -> HTMLResponse:
    """Live shopper-agent → mesh A2A round trip on a fake commerce surface.

    Use case: a judge clicks "Should I buy this?" on a faux pet-store SKU.
    A shopping copilot (vanilla JS, runs in the judge's browser) issues a real
    A2A v0.3 task to /a2a/v1/tasks/send, polls, streams mesh activity in the
    right rail, and makes a recommendation grounded in the signed bundle.

    This is the demo-video centerpiece per docs/SUBMISSION_AUDIT_2026-05-21.md
    Option C. Live page exists so judges can verify; the controlled-conditions
    recording is the primary delivery.
    """
    return HTMLResponse(content=_render_page("shopper-demo.html", active="demo"))


@app.get("/agents", response_class=HTMLResponse)
async def agents_page() -> HTMLResponse:
    """First-class A2A reference for any external agent wanting to call us.

    Stripe-API-Reference shape: 30-second connect quickstart with copy-paste
    curl + Python + TS, in-browser try-it that calls our live mesh, well-known
    endpoints map, signed-bundle output sample, offline signature verification
    snippet, and pricing teaser. The page is also the agent-platform-developer
    pitch surface judges land on when they click `Agents` in primary nav.
    """
    return HTMLResponse(content=_render_page("agents.html", active="developers"))


@app.get("/architecture", response_class=HTMLResponse)
async def architecture() -> HTMLResponse:
    """Standalone architecture diagram surface (Move F per WIN_PLAN.md).

    Serves the SVG inline so judges and reviewers can link to a clean,
    self-contained architecture view that labels all 4 Track 3 mandates.
    """
    svg_path = Path(__file__).parent / "static" / "assets" / "architecture.svg"
    svg = svg_path.read_text(encoding="utf-8")
    nav = _global_nav(active="architecture")
    html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>PawConscious — Architecture</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#0A0B0D">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
{_GLOBAL_CHROME_CSS}
<style>
  :root {{
    --bg: #0A0B0D;
    --bg-elev: #111316;
    --ink: #EDEEF1;
    --muted: rgba(237,238,241,0.62);
    --dim: rgba(237,238,241,0.42);
    --electric: #00D4FF;
    --border: rgba(255,255,255,0.08);
  }}
  * {{ box-sizing: border-box; }}
  body {{ margin:0; padding:0; background:var(--bg); color:var(--ink); font-family:'Geist', ui-sans-serif, system-ui, sans-serif; }}
  .frame {{ max-width:1400px; margin:0 auto; padding:48px 24px 0; }}
  .svg-wrap {{ background:var(--bg-elev); border:1px solid var(--border); border-radius:10px; padding:24px; overflow:hidden; }}
  svg {{ width:100%; height:auto; display:block; }}
  .caption {{ margin-top:28px; padding:20px 24px; background:var(--bg-elev); border:1px solid var(--border); border-radius:8px; }}
  .caption h3 {{ margin:0 0 10px; font-size:13px; font-weight:700; letter-spacing:0.18em; text-transform:uppercase; color:var(--electric); font-family:'JetBrains Mono', ui-monospace, monospace; }}
  .caption p {{ margin:6px 0; font-size:13.5px; line-height:1.6; color:var(--muted); max-width:1100px; }}
  .caption code {{ color:var(--electric); font-family:'JetBrains Mono', ui-monospace, monospace; font-size:12px; }}
</style>
</head><body>
{nav}
<div class="frame">
  <div class="svg-wrap">{svg}</div>
  <div class="caption">
    <h3>How to read this diagram</h3>
    <p><b style="color:var(--ink)">Stage 1 — Reasoning Mesh.</b> The five-agent core. <code>claim-extractor</code> runs first (sequential), then for every claim the orchestrator fans out <code>evidence-grader</code>, <code>vet-rubric</code>, and <code>compliance</code> via <code>asyncio.gather</code>. The <code>auditor</code> merges the evidence and runs an adversarial pre-sign pass. Internal flow is a single-process multi-agent pipeline with public A2A mesh at the edge; ADK migration in progress per the Day-20/21 plan.</p>
    <p><b style="color:var(--ink)">Stage 2 — Sign.</b> The merged <code>EndorsementClaimBundle</code> is canonicalized, signed with <code>Ed25519</code> against <code>did:web:mesh-api-…</code>, and the chain anchor <code>sha256(bundle_hash + ":" + (prev_hash or "genesis"))</code> is appended to the Firestore transparency log.</p>
    <p><b style="color:var(--ink)">Stage 3 — Adversarial.</b> After signing, two agents run in parallel: <code>cert-composer</code> renders the human-readable HTML certificate, and <code>second-opinion</code> uses <code>Gemini 2.5 Pro</code> with <b style="color:var(--ink)">Google Search grounding</b> to run four adversarial stress tests against the conclusion (court, regulator, scientific consensus, public skepticism). Fails CLOSED with <code>UNAVAILABLE</code> when the adversarial pass cannot complete, never silently agreeing.</p>
    <p><b style="color:var(--ink)">A2A v0.3.</b> The public agent card at <code>/.well-known/agent-card.json</code> declares two skills: <code>verify_claim</code> (URL in, signed bundle out) and <code>fetch_substantiation_bundle</code> (PCEC URN in, full bundle out). Our reference <code>ShopperAgent</code> is the live external consumer.</p>
  </div>
</div>
{_GLOBAL_FOOTER_HTML}
</body></html>"""
    return HTMLResponse(content=html)


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
