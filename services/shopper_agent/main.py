"""ShopperAgent — verifiable external A2A consumer (codex G7.3 P0.4).

A separate Cloud Run service that demonstrates an external client calling the
PawConscious Mesh A2A endpoint. Source is in the same MIT public repo so judges
can verify the external A2A call is real, not staged.

Flow:
1. GET /.well-known/agent-card.json on the mesh (discovery)
2. POST /a2a/v1/tasks/send with verify_claim skill (with X-API-Key)
3. Return ranked product list with trust scores attached

For the demo moment in the 3-min video, the founder triggers this against a real
Native Pet / Honest Paws URL while the audience watches the live A2A round-trip
in the log view.

We DO NOT claim Perplexity, Rufus, ChatGPT, or Gemini Shopping have integrated
the protocol (codex G7.3 P0.4). The ShopperAgent is our own consumer demonstrating
the protocol works end-to-end.
"""
from __future__ import annotations

import asyncio
import os
from typing import Any, Optional

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field


MESH_URL = os.environ.get("ACP_MESH_URL", "http://localhost:8080")
MESH_API_KEY = os.environ.get("ACP_MESH_API_KEY", "demo-key-2026-06")
SERVICE_VERSION = "0.1.0"


app = FastAPI(
    title="ShopperAgent — ACP demo consumer",
    version=SERVICE_VERSION,
    description="Demo external A2A consumer for the PawConscious Mesh / ACP demo video.",
)


class ShopRequest(BaseModel):
    intent: str = Field(..., description="User shopping intent (e.g., 'best joint supplement for senior labs')")
    candidate_urls: list[str] = Field(
        default_factory=lambda: ["https://www.nativepet.com/products/hip-joint"],
        description="Candidate product URLs to evaluate via the mesh",
    )
    max_claims_per_product: int = 3


class RankedProduct(BaseModel):
    url: str
    trust_score: float = Field(..., ge=0.0, le=1.0)
    bundle_hash: str
    claims_passed: int
    claims_total: int
    violations: int
    a2a_round_trip_ms: int


class ShopResponse(BaseModel):
    intent: str
    ranked: list[RankedProduct]
    mesh_endpoint: str
    discovery_card_fetched: bool


async def fetch_agent_card(client: httpx.AsyncClient) -> dict[str, Any]:
    """Discovery step — verify mesh advertises verify_claim skill."""
    response = await client.get(f"{MESH_URL}/.well-known/agent-card.json", timeout=15.0)
    response.raise_for_status()
    return response.json()


async def call_verify_claim(client: httpx.AsyncClient, product_url: str, max_claims: int) -> tuple[dict[str, Any], int]:
    """A2A v0.3 async task call to verify_claim.

    Full round-trip (codex C1 P0#2 fix):
      1. POST /a2a/v1/tasks/send → 202 {task_id, poll_url, status: 'submitted'}
      2. Poll /a2a/v1/tasks/get/{task_id} every 5s up to ~5min
      3. Return the completed task response (with output, bundle_hash, signature, chain_anchor)

    Returns (final_response_dict, latency_ms). The dict has the same shape as
    A2ATaskStatusResponse — top-level bundle_hash/bundle_signature/chain_anchor plus
    nested output={claims, vet_scores, compliance, audit, ...}.
    """
    import asyncio
    import time
    payload = {
        "skill": "verify_claim",
        "input": {"product_url": product_url, "max_claims": max_claims},
    }
    headers = {"X-API-Key": MESH_API_KEY, "Content-Type": "application/json"}
    t0 = time.monotonic()

    # Step 1: submit
    submit_resp = await client.post(
        f"{MESH_URL}/a2a/v1/tasks/send",
        json=payload,
        headers=headers,
        timeout=30.0,
    )
    submit_resp.raise_for_status()
    submitted = submit_resp.json()
    task_id = submitted.get("task_id")
    if not task_id:
        raise RuntimeError(f"mesh did not return task_id: {submitted}")

    # Step 2: poll for completion (per A2A v0.3 async lifecycle)
    poll_url = submitted.get("poll_url") or f"{MESH_URL}/a2a/v1/tasks/get/{task_id}"
    max_attempts = 60  # 60 × 5s = 5 min hard cap
    for _attempt in range(max_attempts):
        await asyncio.sleep(5.0)
        get_resp = await client.get(poll_url, timeout=30.0)
        get_resp.raise_for_status()
        task = get_resp.json()
        status = task.get("status")
        if status == "completed":
            latency_ms = int((time.monotonic() - t0) * 1000)
            return task, latency_ms
        if status == "failed":
            raise RuntimeError(f"mesh task failed: {task.get('error', 'unknown')}")
        # else still 'working' — keep polling

    raise TimeoutError(f"mesh task {task_id} did not complete within 5 minutes")


def score_bundle(bundle: dict[str, Any]) -> tuple[float, int, int, int]:
    """Aggregate trust score from EndorsementClaimBundle output."""
    audits = bundle.get("audit", [])
    compliances = bundle.get("compliance", [])
    vet_scores = bundle.get("vet_scores", [])

    if not audits:
        return (0.0, 0, 0, 0)

    pass_count = sum(1 for a in audits if a.get("verdict") == "PASS")
    fail_count = sum(1 for a in audits if a.get("verdict") == "FAIL")
    violations = sum(1 for c in compliances if c.get("violation_flag"))
    total = len(audits)
    avg_vet = sum(v.get("score", 0) for v in vet_scores) / max(len(vet_scores), 1)

    # Trust score: weighted blend of audit pass rate + vet score normalized
    audit_rate = pass_count / total if total else 0.0
    vet_norm = (avg_vet - 1) / 4 if avg_vet >= 1 else 0.0  # map 1-5 → 0-1
    violation_penalty = min(violations * 0.1, 0.5)
    trust = max(0.0, min(1.0, 0.6 * audit_rate + 0.4 * vet_norm - violation_penalty))

    return (trust, pass_count, total, violations)


@app.get("/health")
async def health() -> dict[str, Any]:
    return {"status": "ok", "service": "shopper-agent", "mesh_url": MESH_URL}


@app.post("/shop", response_model=ShopResponse)
async def shop(req: ShopRequest) -> ShopResponse:
    """Demo flow: discover mesh agent card → call verify_claim per candidate → rank by trust."""
    async with httpx.AsyncClient() as client:
        card = await fetch_agent_card(client)
        if not any(s.get("id") == "verify_claim" for s in card.get("skills", [])):
            raise HTTPException(status_code=502, detail="Mesh agent card does not advertise verify_claim")

        ranked: list[RankedProduct] = []
        for url in req.candidate_urls:
            bundle_resp, latency_ms = await call_verify_claim(client, url, req.max_claims_per_product)
            bundle = bundle_resp.get("output", {})
            trust, passed, total, violations = score_bundle(bundle)
            ranked.append(RankedProduct(
                url=url,
                trust_score=trust,
                bundle_hash=bundle_resp.get("bundle_hash", "missing"),
                claims_passed=passed,
                claims_total=total,
                violations=violations,
                a2a_round_trip_ms=latency_ms,
            ))

        ranked.sort(key=lambda r: r.trust_score, reverse=True)
        return ShopResponse(
            intent=req.intent,
            ranked=ranked,
            mesh_endpoint=MESH_URL,
            discovery_card_fetched=True,
        )


@app.get("/")
async def root() -> dict[str, Any]:
    return {
        "service": "ShopperAgent",
        "description": "External A2A consumer demo for PawConscious Mesh. POST /shop with candidate_urls.",
        "mesh": MESH_URL,
        "card_endpoint": f"{MESH_URL}/.well-known/agent-card.json",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.environ.get("PORT", "8081")), reload=False)
