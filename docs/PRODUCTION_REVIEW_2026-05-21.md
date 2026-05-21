# Production Review — 2026-05-21 (PM)

**Audit role:** /review engineer + /devex-review UX lens
**Method:** code-first audit (not narrative), live HTTP probes against GCP APIs, page-by-page IA review against Stripe-grade benchmark
**Live URL audited:** https://mesh-api-oasa5mxega-uc.a.run.app (and local mirror 127.0.0.1:8088)
**Deadline:** 2026-06-05 noon PT (15 calendar days remaining)

---

## TL;DR — what changes if we're shipping a real product, not a hackathon prop

We have a **demo** that scores well. We do not yet have a **product** that holds up to a Stripe-grade rebuttal:

1. **Vertex AI Search corpus is empty.** Every "grounded compliance" call falls through to prompt-only Gemini. Zero data stores exist in the project across all regions. Architecture page + agent card advertise RAG that does not function.
2. **Agent Engine is deployed but not invoked.** Cloud Run runs the mesh inline. The Reasoning Engine resource exists; no production traffic touches it. The "managedReasoningEngine: true" claim is technically true and functionally misleading.
3. **ADK is on one agent of seven.** Track 3 mandates ADK. Only `claim_extractor.py` uses `LlmAgent` + `FunctionTool`. The other six agents are direct `google.genai` calls. Orchestrator is `asyncio.gather`, not ADK `ParallelAgent`.
4. **17/20 eval cases are skipped on dead URLs.** Even with an honest methodology note, "3/3 PASS" optically reads as cherry-picked. Refresh the corpus.
5. **The "mesh" is one Python process.** Internal agents do not speak A2A to each other — they are asyncio coroutines. Only the external surface is A2A. The "mesh" branding overclaims the internal architecture.
6. **Primary nav is inconsistent across pages.** Three of four pages have a different nav (or none). `/architecture` and `/demo/shopper` are not reachable from any global nav — they are URL-discovery only. Stripe never ships this.
7. **Buyer and Developer hero h1 are nearly identical.** Same line, one verb deleted. Two audiences, one message. Stripe's `/` and `/developers` say different things to different people.
8. **Eight sections on the landing page.** `result · architecture · how · proof · biz · moats · founder · track3` overlap conceptually (proof/moat/biz/track3 are all "trust us" variants stacked).

The path to a real product in 15 days is **fewer overclaims, two surgical infrastructure fixes (Vertex Search corpus + ADK migration), and an IA rebuild.** Not more polish on what exists.

---

## Section 1 — Code audit (what is actually running)

### 1.1 ADK presence in the codebase

| Agent | ADK import | Runtime | Notes |
|---|---|---|---|
| `claim_extractor.py` | ✅ `LlmAgent`, `FunctionTool` | scaffold only — `extract_claims()` still calls `google.genai` directly at line 202 | Even the one ADK agent isn't actually invoked through ADK |
| `evidence_grader.py` | ❌ | `genai.Client(vertexai=True)` direct | Calls BioMCP for PubMed retrieval |
| `vet_rubric.py` | ❌ | `genai.Client(vertexai=True)` direct | |
| `compliance.py` | ❌ | `genai.Client(vertexai=True)` direct + Vertex AI Search (broken — see 1.2) | |
| `auditor.py` | ❌ | `genai.Client(vertexai=True)` direct | |
| `report_writer.py` | ❌ | `genai.Client(vertexai=True)` direct | |
| `second_opinion.py` | ❌ | `genai.Client(vertexai=True)` direct + Google Search grounding | |
| `orchestrator.py` | ❌ | `asyncio.gather` | Not `ParallelAgent` / `SequentialAgent` |

**Architecture page already admits this:** "ADK `LlmAgent` is scaffolded on the claim-extractor; the others use `google.genai` direct for deterministic v0.1 latency."

A judge auditing Track 3 compliance reads "scaffolded" as "not deployed." The honesty saves us from accusation. It does not earn points.

### 1.2 Vertex AI Search corpus — **broken in production**

`agents/compliance.py:71`:
```python
VERTEX_SEARCH_DATA_STORE = "acp-regulator-corpus"
```

Live probe results (us, us-central1, eu, global regions, project `pawconscious-mesh-2026` / `40952019806`):

```
global region datastores: 0
us-central1 datastores: 0
eu datastores: 0
us datastores: 0
```

Direct fetch:
```
GET /v1/.../dataStores/acp-regulator-corpus
→ 404 DataStore not found
```

**Consequence:** every call to `retrieve_grounding_sources()` (compliance.py:86) hits the `except Exception` block silently and returns `[]`. The grounding block becomes "(grounding unavailable — using prompt-only knowledge)". The compliance agent runs prompt-only Gemini, which is exactly the hallucination risk the architecture claims to solve.

**Surface claims this is real:**
- Agent card: declares grounded compliance
- `/architecture` page: "Vertex AI Search · provenance with sha256"
- Agent Engine `description` field: "compliance grounded via Vertex AI Search"
- Devpost draft: will lead with this

A judge testing the assertion via inspecting a returned `ComplianceMapping.grounding_sources` array will find it empty.

### 1.3 Agent Engine — deployed but not in traffic path

Reasoning Engine `projects/40952019806/locations/us-central1/reasoningEngines/1255381144908595200` exists (confirmed via API). Pickled object on GCS, `agentFramework: custom`, `displayName: "PawConscious Mesh — ACP for Pet (orchestrator)"`.

But the Cloud Run handler:

```python
# services/mesh_api/main.py:467
async def _run_verify_claim_background(task_id, product_url, max_claims):
    bundle = await run_mesh(product_url, max_claims=max_claims)
    # run_mesh is agents/orchestrator.run_mesh — inline Python asyncio.gather
```

`AGENT_ENGINE_RESOURCE` is referenced only in:
- The health endpoint (`/health/agent-engine`)
- The agent card metadata block

No code path invokes `stream_query` or `query` against the Reasoning Engine in production. The deployed pickle is dead weight relative to traffic.

**Track 3 Key Consideration #5** (multi-agent on Agent Engine) is met on a deployment-existence basis, not a traffic basis. If a judge checks Reasoning Engine call logs in Cloud Console, they see zero.

### 1.4 Mesh ≠ A2A internally

The PCEC pitch is "a mesh of agents talking via A2A." Reality:

```python
# orchestrator.py:38
evidence, vet, comp = await asyncio.gather(
    grade_claim(claim),
    vet_score(claim),
    compliance_map(claim),
)
```

These are direct Python function calls. There is no A2A envelope, no separate process, no network hop between mesh agents. The only A2A surface is the public ingress (`/a2a/v1/tasks/send`) for external callers like the shopper agent.

Calling this a "mesh" is marketing. A judge reading the orchestrator and counting A2A hops finds one (external in, internal `gather`, external bundle out).

### 1.5 Eval cherry-pick risk

`tests/adk_eval/results/latest.json`:
```
total: 20  ·  skipped_url_dead: 17  ·  eligible: 3  ·  passed: 3
```

The HEAD-probe pre-filter (run.py:73) excludes 4xx/5xx URLs from the denominator. **This is methodologically defensible** (real-world DTC catalogs churn) but **optically weak**. A judge clicking through sees three test cases. Three is not a baseline.

Fix paths:
- Refresh URLs to live PDPs (0.5 day work) → eligible jumps to 15-18
- Add synthetic claim fixtures (PDP-text-only, no URL fetch) → 20/20 deterministic
- Both — recommended

### 1.6 Single-instance concurrency

`tests/adk_eval/run.py:84` comment: "mesh runs single-instance, so the GET endpoint can be blocked behind in-flight worker calls."

Real product needs:
- Cloud Run min/max instance config (currently min=1, max likely default)
- Task queue (Cloud Tasks or Pub/Sub) for `_run_verify_claim_background`
- Idempotency key honored (line 535 supports `Idempotency-Key` header — needs verification)

### 1.7 PCEC resolver comment is wrong

`services/mesh_api/main.py:657`:
```python
# PCEC v0 resolver (stub — real implementation in Phase 5 with Firestore)
```

The implementation below it IS Firestore-backed (`fetch_bundle_async`, `get_head_anchor_async`). The "stub" comment is stale and contradicts the working code. A judge code-reviewing reads "stub" and discounts the feature.

### 1.8 max_claims=3 hardcoded

`console-v2.html:1651`: dropdown removed, `max_claims=3` hardcoded.

The eval submits `max_claims=1` (run.py:80). So the live demo runs differently from the eval. Production needs:
- Match: pick one default and use it everywhere
- Expose: rate-tier the parameter (free=1, paid=10, enterprise=unlimited)

### 1.9 `/demo/shopper` honest disclosure

`services/mesh_api/main.py:727` docstring:
> Live shopper-agent → mesh A2A round trip on a fake commerce surface.

The HTML labels it as a faux pet-store SKU. This is the right honest framing. A judge will not mistake it for a real shopper. Acceptable.

---

## Section 2 — UX / IA audit (Stripe-grade lens)

### 2.1 Primary nav is inconsistent across pages

| Page | Primary nav links |
|---|---|
| `/` (Buyers) | Buyers · Developers · Architecture · Agent Engine |
| `/agents` | Buyers · **Agents** · Architecture *(note rename)* |
| `/architecture` | ← Back to PawConscious *(no primary nav)* |
| `/demo/shopper` | PawConscious home · For agents *(custom)* |

**Stripe rule:** the primary nav is identical on every page. The user always knows where they are and how to get to the other things. PawConscious violates this in three of four pages.

Specific bugs:
- "Developers" tab leads to a page labeled "Agents" in its own nav. Pick one name.
- `/architecture` has no primary nav — a judge deep-linking here cannot reach `/agents` or `/`.
- `/demo/shopper` has no global nav at all.

### 2.2 Hero h1 collision

- `/` h1: *"The trust layer AI agents call before recommending a consumer product."*
- `/agents` h1: *"The trust layer to call before recommending a consumer product."*

Same line. One verb deleted. Two audiences, one message.

Stripe's `/` says *"Financial infrastructure for the internet."* Stripe's `/docs` says *"Get started with Stripe."* Different propositions. PawConscious needs the same split:
- `/` (Buyers): *"AI agents will recommend products. Make sure they recommend yours."*
- `/agents` (Developers): *"Add evidence-graded product verification to your agent in 30 seconds."*

### 2.3 Landing page has too many sections that overlap

`/` after the hero:
1. `#result` — cert preview
2. `#architecture` — embedded diagram
3. `#how` — pipeline explainer
4. `#proof` — JFFD case study
5. `#biz` — pricing
6. `.moats` — four-reasons block
7. `.founder` — Omar bio
8. `.track3` — Track 3 badges

Sections 4 (proof), 6 (moats), 7 (founder), 8 (track3) are all variants of "trust us / here's why we're the right team." They stack instead of compose. The buyer reading top-down hits four trust pitches in a row before reaching pricing.

**Stripe-grade buyer pattern** (e.g., `stripe.com/payments`):
1. Hero with one CTA
2. Three product-pillar tiles
3. One "how it works" animation
4. One customer logo bar
5. One pricing tease
6. Footer

PawConscious needs to collapse #proof + #moat + #founder + #track3 into one section ("Why us") with three sub-cards. Eight sections becomes five.

### 2.4 `/architecture` is a dead-end

A judge clicks the Architecture tab → lands on `/architecture` → has no primary nav → only escape is "Back to PawConscious." Cannot reach `/agents` from here. The page is an island.

### 2.5 `/demo/shopper` is undiscoverable

It is the centerpiece of the GFS submission per the audit doc. It is reachable only by knowing the URL or clicking a small CTA on `/`. No primary nav link. After landing on it, a judge cannot navigate to `/agents` or `/architecture` without going back.

Add to primary nav. Probably labeled "Demo" or "Try it." This is the most important page in the submission.

### 2.6 Competing CTAs on `/`

The hero offers:
- Verify URL form
- Cached demo replay
- `/demo/shopper` link
- `/agents` link
- `/architecture` link

Five next-steps. No primary path. A judge with three minutes does not know what to click first.

Stripe rule: **one primary CTA per page**. Everything else is secondary. Pick: is the primary CTA "Try the cached demo" (low friction) or "Go to /demo/shopper" (full flow)? Decide.

### 2.7 No global footer

Stripe's footer is identical on every page: Products · Use cases · Developers · Resources · Company · Legal. Six columns, same on `/` and `/docs`.

PawConscious has no consistent footer. Compliance and trust signals (MIT license, DID, Agent Card, Chain Head, Privacy) should live in a single footer that ships everywhere.

### 2.8 `/agents` page order is documentation, not devex

Current H2 order on `/agents`:
1. Try it from the browser
2. Discovery — well-knowns
3. What we return
4. Verify a signature offline
5. Pricing for agent calls
6. We grade. We don't decide.

Items 5 and 6 are marketing. They belong on `/`. The dev page should be:
1. Hero + one curl that works
2. Try it from the browser (interactive)
3. What we return (response shape)
4. Verify a signature offline
5. Discovery — well-knowns
6. Errors + status codes (missing today)
7. Rate limits + quotas (missing today)

A real developer-reference page has errors + rate limits. PawConscious's does not.

### 2.9 Mobile QA not done

Codex flagged this in earlier audits. Still pending. Stripe-grade products work on mobile by default.

---

## Section 3 — What this becomes as a real production product

If we drop the hackathon frame, the gap list looks like this:

| Layer | What we ship now | What a real product needs |
|---|---|---|
| **Auth** | Single static API key `demo-key-2026-06` | OAuth 2.0 or per-tenant API keys with rotation; key prefix routing |
| **Multi-tenancy** | None (single demo tenant) | Tenant ID on every request, isolated transparency log per tenant |
| **Rate limits** | None | Per-key quotas, 429 with retry-after, usage dashboard |
| **Observability** | Cloud Run logs only | Structured logging, OpenTelemetry traces, latency SLOs, error budget |
| **SLOs** | None published | P50/P95/P99 published; uptime page |
| **Status page** | None | status.pawconscious.com or equivalent |
| **Versioning** | `/a2a/v1`, `/pcec/v0` ad-hoc | Header-based version negotiation, deprecation policy, changelog |
| **Errors** | Plain JSON `{title, detail}` | Problem+JSON (RFC 7807) with stable `type` URIs, machine-readable `code` |
| **Idempotency** | Header accepted, behavior unverified | Tested idempotency window, Stripe-style |
| **Webhooks** | None | Async result delivery via signed webhook + replay |
| **SDK** | curl + Python + TS snippets on `/agents` | Versioned SDKs on PyPI + npm, generated from OpenAPI |
| **OpenAPI** | Not published | Published OpenAPI 3.1 spec at `/openapi.json` |
| **Compliance corpus** | Empty (P0 — see 1.2) | Loaded with FTC §255 + AAFCO + NASC docs; versioned; reindexed on update |
| **Internal A2A** | Asyncio coroutines | Real A2A between separately deployed agents (or honest naming) |
| **Vet panel** | Rubric simulation | Real vet credentials with signed attestations, panel rotation, recusal policy |
| **Pricing infrastructure** | Static page | Stripe checkout, usage metering, billing portal |
| **Legal** | MIT license on repo | ToS, Privacy Policy, DPA template, security.txt |

This is the punch list for the Q3 product, not the GFS submission. Listed here so we know where we are vs. real.

---

## Section 4 — Recommended plan (15 days to ship)

Premise: optimize for **(a) Track 3 compliance**, **(b) judge defensibility**, **(c) UX coherence**. Drop everything else from the audit doc's L-bucket.

### Critical-path remediations (must ship pre-freeze)

| # | Item | Effort | Why |
|---|---|---|---|
| **R1** | **Build the Vertex AI Search corpus.** Create data store `acp-regulator-corpus` in us-central1. Ingest FTC §255 endorsement guides (PDF), AAFCO official labeling guide (PDF/text), NASC quality seal program (HTML). Index. Verify `retrieve_grounding_sources` returns non-empty for a known query. | **1.5 days** | Closes the #1 P0 overclaim. Without this, the Track 3 RAG story is fiction. |
| **R2** | **Wire Reasoning Engine into the live path.** Change `_run_verify_claim_background` to call `reasoning_engine.query(product_url=...)` against the deployed pickle, with a feature flag fallback to inline `run_mesh()` for cold-start latency. Add traffic logs visible at `/health/agent-engine`. | **1 day** | Makes Track 3 Key Consideration #5 real, not aspirational. |
| **R3** | **Migrate evidence_grader + vet_rubric + auditor to ADK `LlmAgent`.** Keep `compliance.py` and `report_writer.py` as direct genai for v0.1 latency, document the choice in `/architecture`. Migrate orchestrator to ADK `ParallelAgent` + `SequentialAgent`. | **2 days** | Track 3 mandate compliance moves from 1/7 → 5/7. Honest line on `/architecture` shrinks. |
| **R4** | **Refresh eval URLs + add synthetic fallback.** Replace dead PDP URLs with live ones (15 brands take ~1 hour to verify), add 5 synthetic fixture cases that don't require URL fetch. Re-run. Target 18+/20 eligible, 16+/20 PASS. | **0.5 day** | Kills the cherry-pick optic. |
| **R5** | **Honest mesh language.** Rename internal `mesh` references in marketing copy where they imply A2A-between-agents. Reserve "mesh" for the public A2A surface + sibling agents (shopper). On `/architecture`, label the internal flow "in-process orchestration over Gemini calls" — accurate. | **0.5 day** | Removes the highest-risk overclaim. |

### IA / UX rebuild (must ship pre-freeze)

| # | Item | Effort | Why |
|---|---|---|---|
| **U1** | **Global nav component.** Single `<nav>` markup included in every page (server-side template). Links: `Buyers · Developers · Demo · Architecture · Docs`. Active state styled. Drop the inline nav from each page's HTML. | **0.5 day** | Stripe-grade IA foundation. |
| **U2** | **Global footer component.** Same approach. Five columns: Product · Developers · Trust (DID, Agent Card, Chain, License) · Company · Legal. | **0.5 day** | Same. |
| **U3** | **Differentiate Buyer hero from Developer hero.** Buyer h1: action-oriented audience-specific. Developer h1: speed-to-first-call (Stripe pattern). Rewrite both. | **0.5 day** | Audience clarity. |
| **U4** | **Collapse landing page from 8 sections to 5.** Merge proof+moat+founder+track3 → one "Why us" section with 4 sub-cards. Keep result + how + biz. | **1 day** | Fixes the "sections overlap" complaint directly. |
| **U5** | **Add Errors + Rate limits to `/agents`.** Two new H2 blocks: HTTP codes table + per-key quota table. Move "Pricing for agent calls" to `/` only. | **0.5 day** | Real devex completeness. |
| **U6** | **Single primary CTA per page.** Decide: `/` primary = "Try cached demo." `/agents` primary = "Run the curl." `/architecture` primary = "View signed bundle." Subordinate everything else. | **0.5 day** | Stripe pattern. |
| **U7** | **Mobile QA pass.** Test landing + /agents + /demo/shopper on iPhone-size viewport. Fix any breakage. | **0.5 day** | Codex carryover. |

### Submission deliverables (carryover from audit doc)

| # | Item | Effort | Status |
|---|---|---|---|
| B1 | Repo public + README polish | 1 day | Pending |
| B2 | Demo video ≤3 min | 2–3 days | Pending |
| B3 | Devpost ~700w text | 1 day | Pending |

### Total day count

R1+R2+R3+R4+R5 = 5.5 days · U1–U7 = 4 days · B1+B2+B3 = 5 days. **Total = 14.5 days.** Deadline is 15 days out. **One-day buffer.**

This is tight. If R3 (ADK migration) blows out, the fallback is R3-lite: migrate only `evidence_grader` and `auditor` (the two with the cleanest LlmAgent shape). 3/7 instead of 5/7. Still beats today's 1/7.

### Suggested day-by-day (subject to codex challenge)

```
Day 17 (2026-05-21 PM, today):
  ✅ Audit complete  · 🔄 Codex handshake (pending) · Start R1 corpus ingestion
Day 18 (05-22): R1 finish (corpus loaded, retrieval verified) · Start U1+U2 (global nav/footer)
Day 19 (05-23): R2 Reasoning Engine wiring · U1+U2 finish
Day 20 (05-24): R3 ADK migration day 1 (evidence_grader + vet_rubric)
Day 21 (05-25): R3 ADK migration day 2 (auditor + orchestrator) · R4 eval refresh
Day 22 (05-26): U3+U4 hero rewrite + landing collapse · R5 honest language pass
Day 23 (05-27): U5+U6+U7 dev-page polish + CTA discipline + mobile QA
Day 24 (05-28): B1 repo public + README polish
Day 25 (05-29): B2 video shoot (centerpiece: shopper demo against rebuilt mesh)
Day 26 (05-30): B2 video edit
Day 27 (05-31): B2 video final
Day 28 (06-01): B3 Devpost draft
Day 29 (06-02): 🔒 DEMO FREEZE · codex final sweep · stranger test
Day 30 (06-03): Absorb stranger findings
Day 31 (06-04): Buffer
Day 32 (06-05): 🚀 SUBMIT by noon PT
```

### Scope cut decision tree

If we slip on any day:
1. **First to cut:** R3 to R3-lite (3/7 not 5/7 ADK).
2. **Next to cut:** U7 mobile QA — accept desktop-only judging.
3. **Next to cut:** U5 Errors + Rate limits on `/agents` — defer to v0.2.
4. **Never cut:** R1 (corpus), R5 (honest language), B1/B2/B3 (submission artifacts).

### Projected score after this plan

| Dimension | Today | After plan | Notes |
|---|---|---|---|
| Technical | 22–24 | 27–29 | R1+R2+R3 close all three Track 3 overclaims |
| Business | 22–24 | 26–28 | B3 articulation + IA clarity |
| Innovation | 14–16 | 16–18 | Real RAG corpus + ADK migration = real evidence of PCEC v0.1 |
| Demo | 12–14 | 18–20 | B2 video + UX rebuild reads as production-grade |
| **Total** | **70–78** | **87–95** | Net +15 vs prior plan's +10 because we fix the substance, not just the framing |

---

## Section 5 — Items to confirm with Omar before execution

1. **R3 scope.** Migrate to 5/7 ADK (target) or 3/7 (safer)?
2. **Corpus scope for R1.** FTC §255 + AAFCO + NASC only, or also add FDA pet food labeling + EU FEDIAF?
3. **Internal mesh renaming for R5.** "Reasoning pipeline" vs "agent orchestrator" vs keep "mesh" with a clarifying footnote?
4. **Demo video centerpiece.** Shopper agent calling rebuilt mesh, or PCEC URN resolution end-to-end? (Audit doc said the former; rebuilt mesh changes the shot list.)
5. **Codex challenge gates.** Run codex after R1+R5 (corpus + honesty) before starting R2+R3? Or after the full critical-path?

---

## Section 6 — Codex handshake (2026-05-21 PM)

**Rating: NEEDS_AMENDMENT. Amendments absorbed below.**

### P0 verifications (codex confirmed all three)

- **1.2 verified.** `VERTEX_SEARCH_DATA_STORE = "acp-regulator-corpus"` (compliance.py:69); retrieval path catches `Exception` and returns `[]` (compliance.py:150); `map_claim` then runs prompt-only with empty `grounding_sources` (compliance.py:158, 192). The 404 is silently swallowed.
- **1.3 verified.** `AGENT_ENGINE_RESOURCE` appears only in the agent card and `/health/agent-engine` (main.py:97, 235). `_run_verify_claim_background` calls `run_mesh` inline (main.py:467, 475) — never the Reasoning Engine `query`.
- **1.4 verified.** Orchestrator fan-out is `asyncio.gather` (orchestrator.py:40, 62). No ADK `ParallelAgent`.

### New findings (codex caught these — I missed them)

- **N1. Fake second skill.** Agent card advertises `fetch_substantiation_bundle` (main.py:185), but `resolve_url_and_skill` at main.py:314 doesn't actually wire it. Only `verify_claim` works. A judge calling the second skill gets silently routed to verify_claim or 404. **P0.**
- **N2. Hardcodes that diverge across surfaces.** Demo key + base URL + `DEFAULT_MAX_CLAIMS=3` in backend (main.py:52, 54, 66). Frontend hardcodes demo key + `max_claims=3` (console-v2.html:2045, 2048; agents.html:293). Eval submits `max_claims=1` (run.py:75). The "site says 3, eval uses 1" divergence will read inconsistent. **P1.**
- **N3. Silent failure cluster.** Four spots fail silently:
  - Vertex Search exception → empty grounding (compliance.py:150)
  - Semantic Scholar enrichment error → zero counts (citation_enricher.py:51)
  - Firestore append failure → logs but UI text says "appended" (main.py:480, console-v2.html:1332)
  - **Second Opinion JSON parse failure → returns `overall_verdict: "CONFIRMS"`** (second_opinion.py:125). The adversarial agent fails OPEN, not CLOSED. This is the worst of the four: an adversarial agent that agrees on every failure mode is not adversarial. **P0.**
- **N4. `/agents` page hardcodes a different base URL** than `PUBLIC_BASE_URL` (agents.html:303). Stale URL on a developer reference page. **P1.**

### Plan amendments (absorbed)

| Original | Amendment |
|---|---|
| **R1** corpus = FTC + AAFCO + NASC in 1.5 days | **R1-amended** — scope to FTC §255 only first (the files already exist in `corpus/ftc-16cfr-255-{0,1,2,3,5}.txt`, 5 files / 112 lines). Add AAFCO + NASC only after FTC ingestion verified. Effort drops to 0.5 day for FTC-only, 1.5 days for full scope. **Licensing note:** FTC is public domain; AAFCO and NASC are private. Re-distributing AAFCO/NASC text in a public repo requires permission. Either link to source URLs without re-distribution, or get permission. |
| **R2** Reasoning Engine wiring in 1 day | **R2-amended** — keep `run_mesh` inline as primary. Add Reasoning Engine `query` behind a feature flag + cold-start p95 gate. Acceptance: if Agent Engine p95 < inline p95 × 2, prefer Agent Engine; else inline. 1.5 days. |
| **R3** ADK migration to 5/7 in 2 days | **R3-amended** — "ADK orchestrator + 2 high-traffic agents in the live path." Migrate `evidence_grader` + `auditor` (the two with cleanest LlmAgent shape). Orchestrator wraps them in `SequentialAgent` + `ParallelAgent`. 3/7 agents on ADK + orchestrator on ADK = honest "built on ADK" claim. Keep "scaffolded" language for the remaining 4 agents. 1.5 days. |
| **R4** eval refresh 0.5 day | **R4-amended** — keep real URLs (refresh 15+ that 404). Add synthetic fixtures as a **separate eval track** (label clearly: "PDP-text-only fixtures, 5/5 deterministic"). Two scoreboards, never merged. 0.5 day. |
| **R5** "in-process orchestration" naming | **R5-amended** — codex says it's accurate, not too humble. Final phrasing: **"single-process multi-agent pipeline (asyncio fan-out), public A2A mesh at the edge."** Use this verbatim on `/architecture`, `/agents`, and in the Devpost. |

### New items (from codex findings)

| # | Item | Effort | Why |
|---|---|---|---|
| **N1** | **Wire `fetch_substantiation_bundle` skill.** Resolve URN from input, fetch from Firestore transparency log, return. Or remove from agent card if scope-cut. | 0.5 day | Fake-thing violation. |
| **N3a** | **Fail-CLOSED for Second Opinion.** On parse error, return `overall_verdict: "UNAVAILABLE"`, not `"CONFIRMS"`. UI shows "second opinion unavailable" badge. | 0.5 hour | The single most product-broken bug in the audit. Adversarial agent that always agrees on failure is worse than no adversarial agent. |
| **N3b** | **UI honesty for Firestore append.** When `append_bundle_async` fails, the cert UI shows "chain anchor unavailable" not "appended." | 1 hour | Match what we say to what we did. |
| **N3c** | **Audit all `except Exception` blocks** for silent paths in the agents/ tree. Either log+raise, or surface in the API response. | 0.5 day | Submission integrity. |
| **N4** | **Single source of truth for `PUBLIC_BASE_URL`.** Template-inject into `agents.html` at render time instead of hardcoding. | 1 hour | Stale URL fix. |

### UX challenge amendments (codex)

- **U3 (Buyer vs Developer hero):** codex agrees they should diverge. Stronger move: shared **headline** ("The trust layer AI agents call before recommending a consumer product") with **divergent subheads**. Buyer subhead = problem-first. Developer subhead = speed-first.
- **U4 (8 sections → 5):** codex agrees Architecture + How can merge into one "How it works" section. Proof + Moats + Founder + Track3 collapse into one "Why trust this" strip with 4 sub-cards. Net: 8 → 4 + post-run cert = 5.
- **IA miss:** No path to "Docs/OpenAPI" or API key acquisition. Add to nav only if those pages exist (don't ship dead links). For v0.1: link "Docs" to `/agents` until we have a separate docs surface.

### Revised total day count

R1-amended (FTC-only) + R2-amended + R3-amended + R4-amended + R5-amended = **5.5 days**
N1 + N3a + N3b + N3c + N4 = **1.25 days**
U1–U7 (UX rebuild) = **4 days**
B1 + B2 + B3 (submission artifacts) = **5 days**

**Total: 15.75 days against a 15-day budget. Over by 0.75 day.**

### Final cuts to fit budget

- **Drop U7 mobile QA** (-0.5 day). Accept desktop-only judging. Mobile is a Q3 item.
- **Drop N1 wire fetch_substantiation_bundle** (-0.5 day). Remove the skill from the agent card instead of wiring it. Honest scope reduction.

**Net: 14.75 days. One-day buffer preserved.**

### Codex final rating: **STRONG (post-amendment).**

Pre-amendment plan was NEEDS_AMENDMENT because of: overscoped R1, optimistic R2, unrealistic R3, naive R4. Post-amendment plan absorbs all five challenges + the four new findings. Highest-risk item to de-risk first per codex: **R1 (corpus ingestion + retrieval verification).** Without it, R3 ADK migration cannot honestly claim grounded compliance.

---

## Section 7 — R1 verification result + Section 1.2 correction

### Audit P0 1.2 was wrong. Retrieval is working in production.

I owe a correction. My initial probe of the Vertex AI Search data store hit the wrong API endpoint (`us-discoveryengine.googleapis.com` with `locations/us`) and reported 0 data stores. The compliance agent code at `agents/compliance.py:70` uses `VERTEX_SEARCH_LOCATION = "global"`. Re-probed against `discoveryengine.googleapis.com` with `locations/global`:

- **Data store `acp-regulator-corpus` exists in global region.** Created 2026-05-18.
- **7 documents indexed** (FTC §255 parts 0-5, AAFCO PF7 summary, NASC quality seal summary).
- **Direct search query returns ranked results with snippets.** 6/7 surface for an endorsement query.
- **Live `/a2a/v1/tasks/send` against `nativepet.com/hip-joint` returns 2 grounding_sources** in the `compliance[0].grounding_sources` array, with real sha256 hashes and real snippet text (AAFCO PF7 + FTC §255.3).

**The compliance agent IS grounding via Vertex AI Search in production.** Section 1.2's headline claim that the corpus is empty and every call falls through to prompt-only was incorrect.

### What this changes

- **R1 effort drops from 0.5 day to ~1 hour.** The corpus exists, retrieval works, no ingestion needed. Remaining R1 work is: (a) bump `max_results` from 3 to 5 in `compliance.py:86` (judges will see thinner grounding than there is), (b) audit `/architecture` page to ensure the Vertex Search story is accurate not aspirational, (c) add a `/health/vertex-search` probe that judges can hit to verify the corpus exists.
- **Track 3 grounding story is intact.** The Devpost claim "grounded compliance via Vertex AI Search" is honest today.
- **The other two P0s still stand.** Agent Engine deployed-but-unused (1.3) and ADK 1/7 (1.4) are both confirmed by codex and remain.

### Budget recovery

R1 was 0.5 day in the post-codex amended plan. Now it's ~1 hour. **0.4 day recovered.** Apply this buffer to: 
- 0.2 day toward R3 (ADK migration) — keep 4/7 scope, more confidence.
- 0.2 day toward unfreeze the second-opinion test path (UNAVAILABLE end-to-end verification).

### Lesson per `feedback_audit_repo_not_narrative`

I audited the code (which was right) but mis-probed the live infrastructure (wrong endpoint). Need to **probe with the exact endpoint/region the code uses, not a guess.** Logging this for the next audit.

