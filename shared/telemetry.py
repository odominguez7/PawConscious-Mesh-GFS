"""Per-agent observability spans for the mesh.

Cloud Run captures stdout to Cloud Logging automatically. Emitting a single
JSON line per agent call gives us a structured trace without depending on
OpenTelemetry or Cloud Trace SDKs. Each span lands as a Cloud Logging entry
with `jsonPayload.span_name`, `duration_ms`, etc., so Log Explorer queries
like `jsonPayload.agent="evidence-grader" AND jsonPayload.outcome="error"`
work out of the box.

Section 6 (2026-05-23) — observability story for Tech 30% / Agent Engine
mandate. Pairs with the existing `_record_latency` gate logic in
services/mesh_api/main.py: this emits PER-AGENT spans, that aggregates them
into the AE vs inline p95 gate.

Usage:

    from shared.telemetry import agent_span

    async def grade_claim(claim):
        async with agent_span("evidence-grader", claim_id=claim.id):
            ...
"""
from __future__ import annotations

import contextlib
import contextvars
import json
import os
import time
from typing import Any, AsyncIterator


_SVC = os.environ.get("ACP_SERVICE_NAME", "mesh-api")
_REV = os.environ.get("K_REVISION", "local")  # Cloud Run sets K_REVISION

# Thread task_id through agent spans without changing
# every call site. Set this once at the top of the verify task handler;
# every span emitted in the same async task picks it up automatically.
_current_task_id: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "pcm_task_id", default=None
)


def set_task_id(task_id: str | None) -> None:
    """Bind task_id to the current async context so subsequent spans
    include it. Call once at the top of the verify task handler."""
    _current_task_id.set(task_id)


def _emit(record: dict[str, Any]) -> None:
    """Write a single JSON line to stdout. Cloud Run routes it to Cloud Logging."""
    record.setdefault("service", _SVC)
    record.setdefault("revision", _REV)
    try:
        print(json.dumps(record, default=str), flush=True)
    except Exception:
        # Telemetry must never block the request path. Swallow.
        pass


@contextlib.asynccontextmanager
async def agent_span(
    agent: str,
    *,
    claim_id: str | None = None,
    extra: dict[str, Any] | None = None,
) -> AsyncIterator[None]:
    """Time an agent call and emit one structured span on exit.

    On success: outcome=ok with duration_ms.
    On exception: outcome=error with exception type + message, then re-raises.
    """
    start = time.perf_counter()
    base: dict[str, Any] = {
        "span_name": "agent_call",
        "agent": agent,
    }
    # Pick up task_id from contextvar if set so all
    # span lines inside a verify task share the same correlation id.
    bound_task = _current_task_id.get()
    if bound_task is not None:
        base["task_id"] = bound_task
    if claim_id is not None:
        base["claim_id"] = claim_id
    if extra:
        base.update(extra)
    try:
        yield
    except Exception as exc:
        base.update({
            "outcome": "error",
            "error_type": type(exc).__name__,
            "error_message": str(exc)[:240],
            "duration_ms": round((time.perf_counter() - start) * 1000, 2),
        })
        _emit(base)
        raise
    else:
        base.update({
            "outcome": "ok",
            "duration_ms": round((time.perf_counter() - start) * 1000, 2),
        })
        _emit(base)


def log_route_decision(path: str, *, task_id: str, gate_open: bool, reason: str) -> None:
    """One log line per request describing whether traffic went via Agent
    Engine or inline asyncio. Pairs with /health/agent-engine-traffic state."""
    _emit({
        "span_name": "route_decision",
        "path": path,
        "task_id": task_id,
        "gate_open": gate_open,
        "gate_reason": reason,
    })
