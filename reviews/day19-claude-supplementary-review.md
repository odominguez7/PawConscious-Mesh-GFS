# Claude supplementary review — Day 19 (v0.14.0)

**Status:** SUPPLEMENTARY ONLY. Codex hit a hard quota error on first attempt. Per locked rule `feedback_codex_handshake_per_move`, this does NOT clear Day 19 — codex must still run. This review is so Omar has a Claude-side signal to compare against codex when quota resets.

**Diff scope:** `origin/main..HEAD` (commit `228a849`). 5 files. 401+/11-.

**Local pytest:** 12 passed / 2 skipped (`@pytest.mark.live`). 9/9 R2 tests in `test_agent_engine_routing.py` green.

## Findings

### [P1] Reasoning Engine query has no timeout
`services/mesh_api/main.py:_run_mesh_via_agent_engine` calls `asyncio.to_thread(engine.query, ...)` with no timeout. If the Reasoning Engine hangs (network partition, model stall), the request waits indefinitely. The p95 gate only fires AFTER a request completes, so a hung request can't trigger the gate to close.

**Fix:** Wrap in `asyncio.wait_for(..., timeout=180.0)` (or env-configurable). On `asyncio.TimeoutError`, call `_record_latency("agent_engine", timeout_ms, succeeded=False)` and fall through to inline.

### [P1] Reasoning Engine return shape mismatch is uncovered by tests
The agent-engine path does `EndorsementClaimBundle(**bundle_json)` assuming the deployed engine returns a JSON dict matching the schema. The 9 R2 tests all mock the agent_engine call. The first time the real `engine.query()` response shape gets exercised is when the flag flips ON in prod.

**Fix:** Wrap the bundle reconstruction in try/except (`pydantic.ValidationError`, `TypeError`, `KeyError`). On parse failure → `_record_latency(succeeded=False)` and fall through to inline. Even better — add an integration test that runs with `ACP_USE_AGENT_ENGINE=true` against the real deployed engine in a CI smoke pass.

### [P2] `AGENT_ENGINE_RESOURCE` parsing is silent on malformed input
`_agent_engine_region()` does `AGENT_ENGINE_RESOURCE.split("/")[1]` and `[3]`. If the env var is misconfigured (bare ID, wrong shape), this raises `IndexError` at the first agent-engine call, not at module load.

**Fix:** Validate format at module load — fail fast.

### [P2] Multi-instance Cloud Run sees per-instance gate state
Latency windows + consec-failure counter + gate state are all process-local. If `mesh-api` scales to 2+ instances, each independently learns its own state. Eventually consistent across rolls but never globally agreed.

**Fix (later):** Same pattern as the chip override fix (R13, 2026-05-19 — Firestore-backed shared state). For Day 19's flag-default-OFF ship, defer. When flag flips ON in staging/prod, revisit.

### [P2] main.py is now 1000+ lines
Day 19 adds ~127 lines. R5 honest-language pass will need to refactor — pull the R2 routing block into its own module (`services/mesh_api/agent_engine_routing.py`).

### [P2] No record_latency call on inline path when it ALSO fails
`_run_verify_claim_background` handles inline exception in the outer `try/except` (already present pre-Day-19) but doesn't call `_record_latency("inline", ..., succeeded=False)`. Asymmetric tracking — only agent_engine accumulates failure counts. Probably intentional (we never auto-open the gate), but worth being explicit.

## Strengths

- ✅ Single `_traffic_gate_lock` (asyncio.Lock) guards all gate state — concurrent reads/writes safe within a process.
- ✅ Codex Day-19 P2 amendment (baseline fallback when inline window is empty) correctly absorbed with live-takes-priority logic.
- ✅ Per-request fallback is clean: agent_engine exception → record failure → flip path to inline → retry inline → task_store communicates the transition.
- ✅ `/health/agent-engine-traffic` is observably comprehensive — judges + operators can see gate state + both p95s + sample counts + failure counter + baseline source without console access.
- ✅ Existing `/health/agent-engine` extended (not replaced), preserves Track 3 Key Consideration #5 wording.
- ✅ U3 hero divergence: `/agents` h1 now matches `/` h1 (shared brand line); both subheads diverged by audience (buyer / integrator). No em dashes. Honors `feedback_writing_style`.

## Recommendation

**Ship Day 19 as-is with flag OFF** (default `_ACP_USE_AGENT_ENGINE_DEFAULT=false`). All shipped changes are either feature-flagged dormant or U3 hero copy (low risk). The [P1] gaps only matter when the flag flips ON.

Before flipping the flag ON in staging/prod (which is NOT planned for Day 19 — that's the runtime decision Omar takes later):

1. Add the timeout (P1.1).
2. Add the parse-failure guard (P1.2).
3. Validate `AGENT_ENGINE_RESOURCE` at module load (P2).
4. Run an integration test against the real deployed engine.

**However:** Day 19 still requires codex CLEAR per the locked rule. This review is not a substitute — it's a complement so Omar can cross-check when codex comes back.
