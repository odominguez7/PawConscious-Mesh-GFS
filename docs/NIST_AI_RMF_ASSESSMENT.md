# NIST AI Risk Management Framework — fit assessment for PawConscious Mesh

**Audience:** GFS judges evaluating Innovation (20% of rubric) + Track 3 differentiation, plus future B2B buyers (General Counsel, Compliance, insurance underwriters) who already speak NIST. **Written:** 2026-05-21. **Status:** initial assessment; full per-action audit on the v0.2 roadmap.

---

## Verdict in three sentences

**Yes, the NIST AI Risk Management Framework (NIST AI 100-1) and its 72-action Playbook are directly applicable to PawConscious Mesh.** The Mesh is an LLM-driven multi-agent system that produces high-consequence claim verdicts a downstream agent will act on. That's exactly the AI system the framework is designed for, and the framework's four functions (Govern · Map · Measure · Manage) and seven trustworthiness characteristics map cleanly onto the architectural choices we already shipped.

This document explains the framework in plain language, maps our existing code to the most relevant Playbook actions, names the gaps, and proposes a roadmap. It is also the first concrete signal we know of in the GFS Track 3 field that a hackathon submission is consciously NIST-aligned.

---

## 1. What the NIST AI RMF is (90-second primer for judges)

The National Institute of Standards and Technology published **AI 100-1 in January 2023** as a voluntary, sector-agnostic framework for managing risks from AI systems. It is now the de-facto reference vocabulary US federal procurement, large enterprise risk teams, and the Office of Management and Budget use when they evaluate AI deployments. The companion **Playbook** ships 72 concrete actions an organization can take to operationalize the framework.

**Two layers matter for this assessment:**

1. **Seven trustworthiness characteristics** an AI system should demonstrate:
   *Valid and reliable · Safe · Secure and resilient · Accountable and transparent · Explainable and interpretable · Privacy-enhanced · Fair (with harmful bias managed).*

2. **Four functions** that organize the 72 actions:
   - **Govern.** Policies, leadership accountability, training, third-party risk.
   - **Map.** Context, scope, business value, scientific integrity, risk-impact assessment.
   - **Measure.** Test/evaluate/validate/verify (TEVV), security, transparency, fairness measurement.
   - **Manage.** Risk treatment, monitoring, incident response, decommissioning.

The Playbook is a checklist. Not every action applies to every system. The point is to pick the relevant ones and operationalize them.

---

## 2. Why PawConscious is exactly the system the framework is designed for

The Mesh:

- Takes a real-world commercial PDP as input.
- Runs an LLM-driven multi-agent reasoning pipeline (4 agents on Google ADK + 3 off by design).
- Returns a **signed verdict** other AI systems will use to decide whether to recommend a product.
- Lives in a regulated domain (FTC §255 endorsement substantiation; AAFCO PF7; NASC public-side standards).
- Has a plaintiff-bar liability surface (Cosequin $11.5M settlement is the live template).

That combination — *LLM reasoning · multi-agent · machine-callable verdict · regulated domain · downstream automation* — is the highest-stakes pattern the RMF was written to govern. Most consumer-facing chatbots are *lower-stakes* than this. So the framework's relevance to PawConscious is unusually high relative to a typical generative-AI hackathon submission.

---

## 3. Where PawConscious already satisfies Playbook actions

This is a working subset, not exhaustive. Each row points at the file or live endpoint that demonstrates the action.

### Govern — already satisfied

| Action | Where shipped | Evidence |
|---|---|---|
| **GOVERN 1.1** Legal and regulatory requirements understood and documented | `agents/compliance.py` maps every claim to FTC 16 CFR §255 + AAFCO PF7 + NASC. `corpus/` holds the public-redistributable source passages. | `/health/vertex-search` returns the live indexed corpus. |
| **GOVERN 1.4** Transparency in process and outcomes | Public chain anchor + signed bundles + did:web + MIT license + public agent card. | [`/.well-known/agent-card.json`](https://mesh-api-40952019806.us-central1.run.app/.well-known/agent-card.json), [`/pcec/v0/chain/head`](https://mesh-api-40952019806.us-central1.run.app/pcec/v0/chain/head) |
| **GOVERN 4.1** Critical-thinking + safety-first design mindset | Multiple rounds of adversarial self-review during development; every blocking finding was resolved before the next change. | git log |
| **GOVERN 4.3** Testing, incident identification, info sharing | Adversarial review per change; `docs/FOLLOWUP_pre_flag_on.md` captures known limits. | Repo public after toggle. |
| **GOVERN 6.1** Third-party risk addressed | `BioMCP`, `Semantic Scholar Graph API`, `Vertex AI Search`, `Firecrawl` are each documented with their failure modes in code comments + N3c audit. | `agents/compliance.py:N3c` block, `agents/claim_extractor.py:N3c` block. |

### Map — already satisfied

| Action | Where shipped | Evidence |
|---|---|---|
| **MAP 1.1** Intended purpose + context + laws documented | `README.md` Track 3 mandate map; `BUSINESS_PLAN.md` buyer + use-case; `docs/PCEC-v0.md` spec scope. | Repo root. |
| **MAP 1.4** Business value defined | `BUSINESS_PLAN.md` tier pricing, ROI ratio, buyer profile, Cosequin template. | [`/`](https://mesh-api-40952019806.us-central1.run.app/) `#biz` section. |
| **MAP 2.3** Scientific integrity + TEVV considerations identified | `agents/auditor.py` ships the Falsifier v0 (citation_existence + claim_direction_match). `tests/adk_eval/cases.json` baseline. `agents/orchestrator.py::describe_mesh_shape` exposes the topology. | [`/health/mesh-shape`](https://mesh-api-40952019806.us-central1.run.app/health/mesh-shape). |
| **MAP 3.4** Operator proficiency + standards documented | `/agents` page is the operator manual. `RUN.md` reproduces locally in 3 commands. | [`/agents`](https://mesh-api-40952019806.us-central1.run.app/agents). |
| **MAP 3.5** Human oversight defined | `vet_rubric` returns `escalate_to_human_vet=true` on ambiguous claims. `attest_expert` A2A skill is the v0.2 roadmap for licensed-DVM attestation. | `agents/vet_rubric.py` |
| **MAP 4.1** Third-party legal-risk mapping | `docs/INDEPENDENCE.md` covers the trust-capture / ISO 17065 question explicitly. Single-issuer at v0.1 with stated migration path to multi-issuer at v0.2. | `docs/INDEPENDENCE.md`. |

### Measure — already satisfied

| Action | Where shipped | Evidence |
|---|---|---|
| **MEASURE 1.1** Metrics selected for measurement | `tests/adk_eval/cases.json` 4 structural assertions per case; eval results in `tests/adk_eval/results/`. | `latest.json` shows the score per run. |
| **MEASURE 2.4** Functionality monitored in production | `/health/agent-engine-traffic` rolling-window p95 + consec-failure counter + traffic-gate state, observable without LLM invocation. | Day 19 R2 ship. |
| **MEASURE 2.5** Limitations of generalizability stated | `agents/auditor.py` labels itself **Falsifier v0** with explicit scope: PMID format + claim-direction only. Cherry-pick detection + sample-size adequacy are post-hackathon. | Code comment + cert HTML. |
| **MEASURE 2.6** Safety risks evaluated | Adversarial `second_opinion` runs 4 stress tests (court, regulator, scientific consensus, public skepticism) on every signed bundle. Fail-CLOSED on parse error per Day 17 N3a. | `agents/second_opinion.py`. |
| **MEASURE 2.7** Security and resilience evaluated | Cloud Run scale-to-zero; rolling p95 + per-request timeout on Agent Engine path; 3-fail consec circuit-breaker; idempotency keys on A2A endpoint. | `services/mesh_api/main.py` R2 block. |
| **MEASURE 2.8** Transparency + accountability examined | Every bundle ships with `chain_anchor_status: "appended" \| "unavailable"` (Day 23 N3b honesty). Issuer DID is `did:web:`. Public transparency log head. | `/a2a/v1/tasks/get/{id}` response shape. |
| **MEASURE 2.9** Model explained + output interpreted in context | Every `ComplianceMapping` carries `grounding_sources` with `snippet_hash` provenance. Every `Evidence` paper has `relevance_score` + `supports_claim_direction` + free-text `notes`. | `shared/pcec_schema.py`. |
### Manage — already satisfied

| Action | Where shipped | Evidence |
|---|---|---|
| **MANAGE 1.4** Negative residual risks documented | `docs/FOLLOWUP_pre_flag_on.md` lists every known P1/P2 that doesn't block ship but is real. `docs/INDEPENDENCE.md` covers the trust-capture risk. | Repo root after public toggle. |
| **MANAGE 2.4** Deactivate AI systems that demonstrate harms | Feature flag pattern (`ACP_USE_AGENT_ENGINE=false` default) + p95 gate auto-close + 3-consecutive-failure circuit-breaker. The Agent Engine path is the riskier path, and it is gated. | Day 19 R2. |
| **MANAGE 3.1** Third-party AI resources monitored | `/health/vertex-search` probes the indexed corpus on every request. `/health/agent-engine` probes the Reasoning Engine. BioMCP + Semantic Scholar errors logged with `type(e).__name__` (Day 23 N3c). | All three `/health/*` probes. |
| **MANAGE 4.3** Incidents communicated to affected actors | A2A task envelope carries `chain_anchor_status: "unavailable"` when the log append fails so the calling agent never reads `null` as "appended" (Day 23 N3b). | `/a2a/v1/tasks/get/{id}`. |

**Subtotal:** 22 of 72 Playbook actions have demonstrable shipped evidence (5 Govern + 6 Map + 7 Measure + 4 Manage). That is unusually high for a 19-day-old codebase.

---

## 4. Where we have honest gaps

The framework is more demanding than a 19-day hackathon can fully satisfy. The honest gaps:

| Action | Gap | Roadmap |
|---|---|---|
| **GOVERN 2.1 / 2.2** Roles + training documented | Solo founder. No internal AI risk training. | Hire #1 = AI safety lead (Y1 H2). |
| **GOVERN 3.1** Diverse decision-making team | Same. | Same. |
| **MAP 1.2** Inter-disciplinary AI actors | Single-founder ship. | Vet panel (`attest_expert`) + accredited certifier partnership = v0.2 + Y1. |
| **MAP 5.1 / 5.2** Likelihood + magnitude of impacts engaged with affected actors | We've thought about brand + plaintiff + AI-shopper impacts. We have NOT formally engaged pet-owner end users in the feedback loop. | Pilot with 3 brands + user-research interviews Y1 H1. |
| **MEASURE 2.10** Privacy risk examined and documented | The mesh handles public PDP content, not user PII. Low risk surface but not formally documented. | Add `docs/PRIVACY_ASSESSMENT.md` v0.2. |
| **MEASURE 3.3** End-user / impacted-community feedback + appeal | The `second_opinion` agent is an internal automated adversarial check, not a user-facing report-and-appeal channel. We have no feedback channel for pet-owner end users or for brands whose claim was flagged. | Add a `/feedback` endpoint + brand-side appeal flow for flagged claims in v0.2. |
| **MEASURE 2.11** Fairness + bias evaluated | No per-claim-kind bias audit. Possible the LLM grades luxury-brand claims more leniently than store-brand — untested. | Add a fairness sub-eval to `tests/adk_eval/` v0.2. |
| **MEASURE 2.12** Environmental impact / sustainability | Gemini API call counts not tracked. | Add token-usage telemetry v0.2. |

None of these block submission. All are real follow-ups.

---

## 5. Strategic value

### For the GFS hackathon (Innovation 20%)

The Innovation dimension of the rubric rewards novelty in approach, not just feature surface. Most Track 3 submissions are agentic apps with no formal risk-management posture. A submission that says:

> "We mapped 22 of NIST AI RMF Playbook's 72 actions to shipped code, with `/health/mesh-shape` + `/health/agent-engine-traffic` + `chain_anchor_status` exposing the framework's transparency and accountability requirements at the HTTP layer"

reads as an order-of-magnitude more thoughtful than:

> "We built a chatbot with tool-calling."

This is concrete differentiation against the field of 401+ Devpost idea pages.

### For post-hackathon B2B sales

The B2B buyer (General Counsel · Head of Compliance · CMO) already speaks NIST. So do insurance underwriters, accredited certifiers (NASC, NSF), and any vet-school partnership office. Saying "we are NIST AI RMF aligned" is a credibility shortcut that compresses what would otherwise be a 30-minute "what is your AI risk posture" call into a 30-second statement and a link to this document.

### For PCEC v0.1 → v0.2 spec evolution

The seven trustworthiness characteristics map directly onto PCEC bundle fields we could add as v0.2:

| RMF characteristic | Proposed PCEC v0.2 field |
|---|---|
| Valid + reliable | `evidence_strength_score` (already implicit in per-paper `relevance_score`; promote to bundle-level) |
| Safe | `second_opinion.overall_verdict` + per-stress-test `second_opinion.tests[].verdict` (already shipped — `agents/second_opinion.py` returns CONFIRMS \| NEEDS REVIEW at the bundle level plus four per-test SURVIVES \| NEEDS REVIEW verdicts) |
| Secure + resilient | `signing_key_provenance` (HSM vs software; document trust anchor) |
| Accountable + transparent | `chain_anchor` + `chain_anchor_status` (already shipped) |
| Explainable + interpretable | `grounding_sources[].snippet_hash` (already shipped) |
| Privacy-enhanced | `pii_scan_result` (NEW — confirm no PII leaked into the bundle) |
| Fair (bias managed) | `claim_kind_distribution` + `brand_class` (NEW — for fairness audit) |

That turns "PCEC is a verifiable claim spec" into "**PCEC is the only consumer-trust spec aligned to NIST AI RMF trustworthiness characteristics**." That is a stronger pitch to the Linux Foundation donation path on the Y3 roadmap.

---

## 6. Recommendation

1. **Land this assessment in the repo before Devpost submission.** Cost: zero, beyond the time to write this file. Benefit: real Innovation lift + B2B credibility moat.
2. **Add a one-line callout in the README** ("Innovation: NIST AI RMF posture") that links here. Subtle enough to not look like buzzword-padding; clear enough for the judge who notices.
3. **Promote the seven trustworthiness fields into the PCEC v0.2 spec** as a post-hackathon work item.
4. **Pull this assessment into the Devpost "What we learned" field** as a single sentence: *"We mapped 22 of 72 NIST AI RMF Playbook actions to shipped code; see [`docs/NIST_AI_RMF_ASSESSMENT.md`](docs/NIST_AI_RMF_ASSESSMENT.md)."*

The framework is not just useful — for PawConscious specifically, alignment with it is the most defensible Innovation differentiator available to us in the 14 days remaining.

---

## Source files

- **Framework JSON:** [`docs/nist_ai_rmf/Artificial Intelligence Risk Management Framework.json`](nist_ai_rmf/Artificial%20Intelligence%20Risk%20Management%20Framework.json) (44 sections, 120K chars of source text, NIST AI 100-1, January 2023).
- **Playbook JSON:** [`docs/nist_ai_rmf/nist_ai_rmf_playbook.json`](nist_ai_rmf/nist_ai_rmf_playbook.json) (72 actions across Govern/Map/Measure/Manage).
- **Original PDF:** [`docs/nist_ai_rmf/NIST.AI.100-1.pdf`](nist_ai_rmf/NIST.AI.100-1.pdf).
- **Public:** https://www.nist.gov/itl/ai-risk-management-framework

Both JSON files live in the repo for reproducibility; the structured form is for programmatic cross-reference with future audit tooling.
