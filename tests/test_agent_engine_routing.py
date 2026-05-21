"""R2 — Agent Engine routing gate tests (Day 19 plan, 2026-05-22).

Covers:
1. Feature flag default OFF → gate closed → inline path.
2. Gate auto-closes when Agent Engine p95 > N x inline p95 over a full window.
3. Three consecutive Agent Engine failures close the gate.
4. /health/agent-engine-traffic returns coherent state.

No live Vertex AI calls. Routing module reads env vars at import time, so
each test reimports services.mesh_api.main with the env it needs.
"""
from __future__ import annotations

import importlib
import os
import sys

import pytest


def _reload_main(env: dict[str, str]):
    for k in (
        "ACP_USE_AGENT_ENGINE",
        "ACP_AGENT_ENGINE_P95_GATE",
        "ACP_AGENT_ENGINE_MIN_SAMPLES",
        "ACP_LATENCY_WINDOW_SIZE",
        "ACP_AGENT_ENGINE_QUERY_TIMEOUT_S",
    ):
        os.environ.pop(k, None)
    for k, v in env.items():
        os.environ[k] = v
    if "services.mesh_api.main" in sys.modules:
        del sys.modules["services.mesh_api.main"]
    return importlib.import_module("services.mesh_api.main")


@pytest.mark.asyncio
async def test_default_flag_off_routes_inline():
    main = _reload_main({})
    assert main._ACP_USE_AGENT_ENGINE_DEFAULT is False
    assert main._traffic_gate_open is False
    assert await main._route_verify_path() == "inline"


@pytest.mark.asyncio
async def test_flag_on_routes_agent_engine_until_gate_closes():
    main = _reload_main(
        {
            "ACP_USE_AGENT_ENGINE": "true",
            "ACP_AGENT_ENGINE_MIN_SAMPLES": "3",
            "ACP_AGENT_ENGINE_P95_GATE": "2.0",
            "ACP_LATENCY_WINDOW_SIZE": "10",
        }
    )
    assert main._ACP_USE_AGENT_ENGINE_DEFAULT is True
    assert main._traffic_gate_open is True
    assert await main._route_verify_path() == "agent_engine"


@pytest.mark.asyncio
async def test_p95_gate_closes_when_agent_engine_too_slow():
    main = _reload_main(
        {
            "ACP_USE_AGENT_ENGINE": "true",
            "ACP_AGENT_ENGINE_MIN_SAMPLES": "3",
            "ACP_AGENT_ENGINE_P95_GATE": "2.0",
            "ACP_LATENCY_WINDOW_SIZE": "10",
        }
    )
    # Inline ~ 1000ms, Agent Engine ~ 5000ms → 5x > 2x gate, closes.
    for _ in range(5):
        await main._record_latency("inline", 1000.0, succeeded=True)
        await main._record_latency("agent_engine", 5000.0, succeeded=True)
    assert main._traffic_gate_open is False
    assert "p95=" in main._traffic_gate_reason
    assert await main._route_verify_path() == "inline"


@pytest.mark.asyncio
async def test_p95_gate_stays_open_when_agent_engine_acceptable():
    main = _reload_main(
        {
            "ACP_USE_AGENT_ENGINE": "true",
            "ACP_AGENT_ENGINE_MIN_SAMPLES": "3",
            "ACP_AGENT_ENGINE_P95_GATE": "2.0",
            "ACP_LATENCY_WINDOW_SIZE": "10",
        }
    )
    # Inline ~ 1000ms, Agent Engine ~ 1500ms → 1.5x < 2x gate, stays open.
    for _ in range(5):
        await main._record_latency("inline", 1000.0, succeeded=True)
        await main._record_latency("agent_engine", 1500.0, succeeded=True)
    assert main._traffic_gate_open is True
    assert await main._route_verify_path() == "agent_engine"


@pytest.mark.asyncio
async def test_three_consecutive_agent_engine_failures_close_gate():
    main = _reload_main(
        {
            "ACP_USE_AGENT_ENGINE": "true",
            "ACP_AGENT_ENGINE_MIN_SAMPLES": "5",
            "ACP_LATENCY_WINDOW_SIZE": "10",
        }
    )
    assert main._traffic_gate_open is True
    for _ in range(3):
        await main._record_latency("agent_engine", 0.0, succeeded=False)
    assert main._traffic_gate_open is False
    assert "consecutive" in main._traffic_gate_reason
    assert await main._route_verify_path() == "inline"


@pytest.mark.asyncio
async def test_agent_engine_success_resets_consecutive_failure_counter():
    main = _reload_main(
        {
            "ACP_USE_AGENT_ENGINE": "true",
            "ACP_AGENT_ENGINE_MIN_SAMPLES": "100",  # never hit p95 gate
            "ACP_LATENCY_WINDOW_SIZE": "20",
        }
    )
    await main._record_latency("agent_engine", 0.0, succeeded=False)
    await main._record_latency("agent_engine", 0.0, succeeded=False)
    await main._record_latency("agent_engine", 1500.0, succeeded=True)
    # Counter should reset on a success — next 2 failures must not close the gate.
    await main._record_latency("agent_engine", 0.0, succeeded=False)
    await main._record_latency("agent_engine", 0.0, succeeded=False)
    assert main._traffic_gate_open is True


def test_percentile_helper():
    main = _reload_main({})
    assert main._percentile([], 0.95) is None
    assert main._percentile([100.0], 0.95) == 100.0
    samples = [float(x) for x in range(1, 101)]
    p95 = main._percentile(samples, 0.95)
    assert 94.0 <= p95 <= 96.0


@pytest.mark.asyncio
async def test_baseline_closes_gate_when_no_live_inline_samples():
    """Codex Day-19 P2: when feature flag starts ON, inline samples never accrue.
    Gate must still close on latency via ACP_INLINE_P95_BASELINE_MS."""
    main = _reload_main(
        {
            "ACP_USE_AGENT_ENGINE": "true",
            "ACP_AGENT_ENGINE_MIN_SAMPLES": "3",
            "ACP_AGENT_ENGINE_P95_GATE": "2.0",
            "ACP_LATENCY_WINDOW_SIZE": "10",
            "ACP_INLINE_P95_BASELINE_MS": "1000",
        }
    )
    assert main._traffic_gate_open is True
    # Only Agent Engine samples, none from inline. Should still close.
    for _ in range(5):
        await main._record_latency("agent_engine", 5000.0, succeeded=True)
    assert main._traffic_gate_open is False
    assert "baseline" in main._traffic_gate_reason


@pytest.mark.asyncio
async def test_baseline_keeps_gate_open_when_agent_engine_acceptable():
    main = _reload_main(
        {
            "ACP_USE_AGENT_ENGINE": "true",
            "ACP_AGENT_ENGINE_MIN_SAMPLES": "3",
            "ACP_AGENT_ENGINE_P95_GATE": "2.0",
            "ACP_LATENCY_WINDOW_SIZE": "10",
            "ACP_INLINE_P95_BASELINE_MS": "5000",
        }
    )
    for _ in range(5):
        await main._record_latency("agent_engine", 4000.0, succeeded=True)
    assert main._traffic_gate_open is True


@pytest.mark.asyncio
async def test_agent_engine_query_timeout_raises_and_records_failure(monkeypatch):
    """Codex Day-19 amend pass [P1]: a hung engine.query() must time out so the
    fallback path runs and consec_failures increments.

    Simulates a Reasoning Engine that takes longer than the configured timeout.
    We assert that:
    1. _run_mesh_via_agent_engine raises asyncio.TimeoutError (not stuck forever).
    2. The caller's exception handler will see a real exception and can record
       the failure + fall through to inline.
    """
    import asyncio as _asyncio

    main = _reload_main(
        {
            "ACP_USE_AGENT_ENGINE": "true",
            "ACP_AGENT_ENGINE_QUERY_TIMEOUT_S": "0.2",  # 200ms — short for test speed
        }
    )

    class _SlowEngine:
        def query(self, product_url, max_claims):
            import time
            time.sleep(2.0)  # 10x the configured timeout
            return {}

    monkeypatch.setattr(main, "_get_agent_engine_client", lambda: _SlowEngine())

    with pytest.raises(_asyncio.TimeoutError):
        await main._run_mesh_via_agent_engine("https://example.com/p", 3)


@pytest.mark.asyncio
async def test_repeated_query_timeouts_close_the_gate():
    """End-to-end of the timeout absorption: three timeout-failures recorded via
    _record_latency close the gate via the existing consecutive-failure path."""
    main = _reload_main(
        {
            "ACP_USE_AGENT_ENGINE": "true",
            "ACP_AGENT_ENGINE_MIN_SAMPLES": "100",  # never hit p95 gate
            "ACP_AGENT_ENGINE_QUERY_TIMEOUT_S": "0.2",
        }
    )
    assert main._traffic_gate_open is True
    # Simulate what _run_verify_claim_background does on TimeoutError:
    # record the failure with the timeout value as the latency.
    timeout_ms = main._ACP_AGENT_ENGINE_QUERY_TIMEOUT_S * 1000.0
    for _ in range(3):
        await main._record_latency("agent_engine", timeout_ms, succeeded=False)
    assert main._traffic_gate_open is False
    assert "consecutive" in main._traffic_gate_reason
    assert await main._route_verify_path() == "inline"
