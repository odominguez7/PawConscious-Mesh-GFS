# Pre-flag-ON follow-ups for R2 Agent Engine routing

**Status:** Day 19 shipped with `ACP_USE_AGENT_ENGINE=false` (default). When you decide to flip the flag ON in staging or prod, complete these first.

## [P1] Reasoning Engine return-shape coverage

Flagged by Claude cross-review 2026-05-21, NOT flagged by codex (different judgment). Real risk surface when the flag flips ON.

**The risk:**
`_run_mesh_via_agent_engine` does `EndorsementClaimBundle(**bundle_json)` assuming the deployed Reasoning Engine's `engine.query()` returns a JSON dict matching the pydantic schema. The 9+2 R2 routing tests all mock the agent_engine call. The first real exercise of the response shape happens the first time the flag flips ON.

**Fix:**

```python
# In services/mesh_api/main.py _run_mesh_via_agent_engine
from pydantic import ValidationError

async def _run_mesh_via_agent_engine(product_url: str, max_claims: int) -> EndorsementClaimBundle:
    engine = await asyncio.to_thread(_get_agent_engine_client)
    bundle_json = await asyncio.wait_for(
        asyncio.to_thread(engine.query, product_url, max_claims),
        timeout=_ACP_AGENT_ENGINE_QUERY_TIMEOUT_S,
    )
    try:
        return EndorsementClaimBundle(**bundle_json)
    except (ValidationError, TypeError, KeyError) as parse_err:
        # The existing exception handler in _run_verify_claim_background will catch
        # this, record the failure, and fall through to inline. Re-raise as a
        # distinguishable error type so the gate-failure reason is clear.
        raise RuntimeError(
            f"agent_engine returned malformed bundle JSON: {type(parse_err).__name__}: {parse_err}"
        ) from parse_err
```

Add a test analogous to `test_agent_engine_query_timeout_raises_and_records_failure` that monkey-patches `_get_agent_engine_client` to return an engine whose `.query()` returns `{}` (or any malformed shape), and asserts `RuntimeError` is raised.

## [P2] Resource format validation at module load

`_agent_engine_region()` parses `AGENT_ENGINE_RESOURCE.split("/")` and indexes `[1]` (project) + `[3]` (location). A misconfigured env var (bare ID, wrong shape) raises `IndexError` at the first agent-engine call, not at module load.

**Fix:** add `assert len(parts) >= 5 and parts[0] == "projects" and parts[2] == "locations"` after the split, with a clear error message, called once at module load via a validator function.

## [P2] Multi-instance Cloud Run shared gate state

Latency windows + gate state + consec-failure counter are process-local. If `mesh-api` scales to 2+ instances, each independently learns its own state — same root cause as the chip-override fix (R13, 2026-05-19, Firestore-backed shared state).

**Fix when the flag flips ON in prod:** promote `_traffic_gate_open`, `_traffic_gate_reason`, `_latency_*_ms`, and `_agent_engine_consec_failures` to a Firestore-backed shared store (mirror the chip-override pattern).

## [P2] main.py size

Day 19 added ~150 lines to a file already 1000+ lines long. R5 honest-language pass should pull the R2 routing block into `services/mesh_api/agent_engine_routing.py`.

## [P2] Asymmetric inline-failure tracking

`_record_latency` only tracks failures for `path == "agent_engine"`. Inline failures don't increment any counter. Intentional (we never auto-open the gate) but worth documenting explicitly in the function docstring.
