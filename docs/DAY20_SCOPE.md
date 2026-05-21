# Day 20 scope — R3 ADK migration day 1 + U4 landing collapse

Written 2026-05-21 PM autonomously while Day 19 awaits codex CLEAR (quota hit).

## R3 — ADK migration day 1 (1 day budgeted)

Target: 4 agents on ADK (orchestrator + claim_extractor + evidence_grader + compliance + auditor). Day 19 already shipped orchestrator/claim_extractor in the locked plan; day 20 focuses on **evidence_grader, auditor**, and the SequentialAgent/ParallelAgent wrappers.

### Files to touch

| File | Current shape | Day 20 change |
|---|---|---|
| `agents/orchestrator.py` (115L) | `asyncio.gather` fan-out + sequential auditor at L40-47 | Wrap as `ParallelAgent` (evidence + vet + compliance) feeding into `SequentialAgent` (parallel → auditor). Keep `asyncio.gather` as the inner fallback for non-ADK execution. |
| `agents/evidence_grader.py` (225L) | Direct `genai.Client` calls + BioMCP `search_articles` | `LlmAgent` + `FunctionTool` wrapping `search_pubmed` (already exists as `_search_articles_async`). Preserve `enrich_with_citations` flow as a second `FunctionTool`. |
| `agents/auditor.py` (164L) | Direct `genai.Client` with `AUDIT_PROMPT` | `LlmAgent` carrying the same prompt + same gemini-2.5-flash model. No new tools (it's prompt-only adversarial check on EvidenceBundle). |
| `services/mesh_api/main.py` | Currently calls `run_mesh()` inline | Add ADK runner path behind existing `ACP_USE_AGENT_ENGINE` flag — but for day 20 just wire the wrappers, NOT route prod traffic. |

### Risk surface

- **vet_rubric + report_writer + second_opinion stay direct genai** (locked decision 2026-05-21 — 4/7 ADK is the honest claim, not 7/7).
- **`ParallelAgent` doesn't accept arbitrary coroutines** — it wants `LlmAgent` instances. The current `process_claim` returns 4 tuples from 4 different agents; the ADK shape will need a result-merging step. Probably an `output_key` on each child + manual merge in a SequentialAgent step.
- **BioMCP tool injection**: `FunctionTool` needs an async-safe wrapper. Today's `_search_articles_async` already returns coroutines; verify ADK passes args correctly.
- **Test surface**: Day 19 added 9 R2 routing tests. Day 20 needs ADK structural tests (wrapper instantiation, output_key contracts) without requiring live Agent Engine — mock the ADK runner.

### Verification path
1. Local pytest stays green (no live ADK call required).
2. `/health/mesh-shape` (new probe) returns `{"orchestrator": "SequentialAgent", "parallel_branch": [...], "agents_on_adk": 4}` — judges + devpost can curl it.
3. Codex handshake before EOD.

## U4 — landing collapse (1 day budgeted, target 9 → 5 sections on `/`)

### Section audit (today, 2026-05-21)
Reading `services/mesh_api/static/console-v2.html`:

| # | Selector | Keep / merge / drop |
|---|---|---|
| 1 | `<section class="hero" id="top">` | KEEP |
| 2 | `<section class="result-report" id="result">` | KEEP (hidden by default; shows after cert run) |
| 3 | `<section class="arch" id="architecture">` | MERGE → `#how-it-works` |
| 4 | `<section class="how" id="how">` | MERGE → `#how-it-works` |
| 5 | `<section class="proof" id="proof">` | MERGE → `#why-trust-this` |
| 6 | `<section class="biz" id="biz">` | KEEP |
| 7 | `<section class="moats">` | MERGE → `#why-trust-this` |
| 8 | `<section class="founder">` | MERGE → `#why-trust-this` |
| 9 | `<section class="track3">` | MERGE → `#why-trust-this` |

Result: 5 sections — `#hero`, `#result`, `#how-it-works`, `#why-trust-this`, `#biz`.

### Sub-card structure inside `#why-trust-this`
Per plan: 4 sub-cards.
1. **Proof** (from `.proof`) — JFFD cert example + signed-bundle viewer.
2. **Moat** (from `.moats`) — 4 moats: vet panel, non-comp, OTC-only, Boston wedge.
3. **Founder** (from `.founder`) — Omar + Jennifer Fremont Smith credibility.
4. **Track 3** (from `.track3`) — A2A + Agent Engine + Vertex Search + ADK pillars (judges).

### Risk surface
- **Nav anchors break**: `#proof`, `#how`, `#architecture` are referenced from primary nav and footer. Add anchor redirects in JS, OR keep IDs on sub-divs inside the merged sections so `#proof` still scrolls correctly.
- **Visual rhythm**: collapsing 4 sections into 4 sub-cards risks a wall of text. Honor `feedback_pawconscious_audience_test` — 15-year-old + VC + pet owner all need to read it.
- **No em dashes** (feedback_writing_style).

### Verification path
1. Visual diff in gstack browser at 1280x800 + responsive 376x800.
2. Click every primary-nav + footer anchor on the page — none should 404.
3. Codex handshake before EOD.

## Day 19 close-out (blocking)

Day 20 cannot start until Day 19 clears codex. Status as of 2026-05-21 PM:
- Local pytest: 12 passed / 2 skipped (live-marked).
- Codex review: blocked on quota.
- Push + deploy + browser verify: blocked on codex CLEAR.
- Before-state captured: `reviews/day19-before/` (2 PNG + 3 JSON).

Next action: retry codex when quota resets, then push / deploy / verify.
