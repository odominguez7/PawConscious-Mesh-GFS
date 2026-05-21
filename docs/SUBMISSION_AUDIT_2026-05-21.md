# Submission Audit — 2026-05-21

**Status:** 15 days to deadline (2026-06-05, 5 PM PT)
**Audit method:** /devex-review against live URL with GFS-rubric lens + git/file/HTTP probes
**Audit commit:** `ea81958` (v0.10.4)
**Live URL audited:** https://mesh-api-oasa5mxega-uc.a.run.app/

---

## TL;DR — the five blockers between us and shipping

1. **🚨 API-key gate blocks judges by default** — every A2A call returns 401 without `X-API-Key: demo-key-2026-06`. `services/mesh_api/main.py:412`. The README mentions the key but does not put it where a Devpost reader will look. If the demo key is not the FIRST thing on the Devpost page, a judge fails the very first POST and walks away. Codex flagged this as worse than the shape mismatch. (Audit amendment 2026-05-21 post-codex)
2. **🚨 ADK eval shows 0/1 passing (0%)** — README badge softly says "baseline spec live" but a curious judge clicking through `tests/adk_eval/results/latest.json` sees `"passed": 0, "score": "0/1", "pct": 0.0`. Need to run all 20 cases against the deployed mesh, get an actual PASS rate, and either fix what's broken or remove the badge.
3. **🚨 A2A endpoint accepts the wrong shape** — agent card declares A2A v0.3, but POST `/a2a/v1/tasks/send` with the standard A2A envelope (`params.message.parts[].text`) returns HTTP 422. It only accepts a custom flat `{skill, input}` shape. Track 3 mandate is A2A; a judge testing standards compliance fails the first call.
4. **🚨 Repo is STILL PRIVATE** — submission rules require a public OSI-licensed repo with link visible at the top of the project page. Three "Repo ↗" links in the UI 404 for anyone but the owner.
5. **🚨 No demo video** — required artifact. ≤3 min, English, YouTube/Vimeo public. Not started.

These are blockers, not nice-to-haves. Each one fails a submission requirement or a Track 3 mandate.

---

## Where we are honestly

Today is day 16 of 19 since project started (2026-05-17). The plan claims 9 moves to 100/100; 4 days of the last 5 went into v0.10.x visual polish on the buyer hero. **Plan ≠ work.** That's not necessarily wrong (the hero needed it), but Moves C/D/E/G all read `pending` in WIN_PLAN and none shipped this week.

What did ship: a buyer-hero page that scores 8/10 on a prior devex-review (2026-05-21 05:11 UTC), a cached demo that mostly works, real Ed25519 signatures and Firestore chain anchors, and a working `/architecture` route. **The product surface is good. The submission package is not.**

---

## Live audit — what a judge actually sees

**Tab 1: landing page.** Page loads in 1s. Hero copy reads cleanly. Three "Repo ↗" links — all 404 (private). Footer Track 3 badges (B2B, Cloud Run, Gemini, ADK, A2A v0.3, Agent Engine) are present. Architecture link works.

**Tab 2: cached demo.** Click "▶ Replay cached demo" → 16 stream lines populate `#demoStream`. Verdict ribbon shows "COURT ✓ · REGULATOR ⚠ · CONSENSUS ⚠ · PUBLIC ⚠". Real JFFD URN `urn:pcec:claim:syrz7izwfbatx6go2hgn2ipy` renders in the `#result` section far below the fold. **But the inline `#demoCert` placeholder in the hero still shows dashes** — `verdict— bundle_urn— bundle_hash— chain_anchor— signature—`. A judge looking at the hero result panel after the demo "completes" sees an empty cert template above the real cert. Visual regression from v0.10.3 cert relocation.

**Tab 3: /architecture.** Loads. Content is honest: "Custom prompt-only. NOT ADK Eval (datasets not built in 18 days)." That's the right tone, not overclaim. Names the 7 agents, 3 stages, declares all 4 Track 3 mandates met.

**Tab 4: /.well-known/agent-card.json.** Valid. Declares A2A v0.3, references the Reasoning Engine resource, two skills (`verify_claim`, `fetch_substantiation_bundle`).

**Tab 5: /.well-known/did.json.** Valid did:web with Ed25519 multibase key.

**Tab 6: /pcec/v0/chain/head.** Returns real chain anchor `sha256:5fb540b6...`.

**Tab 7: POST /a2a/v1/tasks/send with A2A v0.3 standard envelope.** HTTP 422. **Endpoint demands `{skill, input}` not `params.message.parts`.** This is broken for any standards-compliant A2A consumer.

**Tab 8: github.com/odominguez7/PawConscious-Mesh-GFS.** 404. Repo private.

---

## Rubric scoring (today's reality, not the plan's projection)

| Dimension | Weight | Plan claim | Audit reality | Gap to ceiling |
|---|---|---|---|---|
| Technical | 30% | 26–28 / 30 | **22–24 / 30** | A2A spec shape mismatch (-2), ADK runtime still claimed as scaffold not runtime (-2), eval 0/1 pass (-2) |
| Business | 30% | 22–24 / 30 | **22–24 / 30** | Plan matches reality here. Buyer hero + pricing + four-reason moat block live. Needs Devpost text (J). |
| Innovation | 20% | 16–17 / 20 | **14–16 / 20** | PCEC v0.1 spec lives in `docs/PCEC-v0.md` but no standalone repo, no signal anyone outside the project has seen it. |
| Demo | 20% | 17–19 / 20 | **12–14 / 20** | Video does not exist (-5), architecture diagram good (+1), cert UX regression in hero (-1), repo private blocks judge-browses-code (-1). |
| **Total** | | **~81–88** | **~70–78** | **~12 points of recoverable lift in 15 days** |

**The plan is overstating Demo by ~5 points.** Video is the big one. Everything else is fixable.

---

## What's broken or doesn't make sense

### Broken

1. **A2A v0.3 envelope rejection.** `services/mesh_api/main.py:398` accepts a flat `A2ASubmittedRequest` Pydantic model with required `skill` and `input` fields. The A2A v0.3 spec uses `params.message.parts[].text`. If a judge runs an A2A test agent against the public card, they get HTTP 422 on first call. Either accept both shapes, or document the custom shape in the agent card.
2. **Hero `#demoCert` placeholder.** v0.10.3 moved the real cert out of the hero container into a separate `section.result-report#result` below the fold, but left the in-hero `#demoCert` element with dashes. After the cached cycle "completes" the hero shows an empty cert; the real cert is 4-5 scroll-screens below. Either hide the placeholder when cycle completes, or render the cert summary in the hero.
3. **README badge links to `mesh-api-40952019806.us-central1.run.app`.** That URL is one of two Cloud Run hostnames; the alt is `mesh-api-oasa5mxega-uc.a.run.app`. Both work today, but DID is bound to the project-number form. If we ever map a custom domain, the existing badges are stale. Not blocking, but worth fixing pre-submission.
4. **ADK eval `results/latest.json` shows 0/1.** Either the May 20 run was a smoke test (1 case) that genuinely failed, or it was a dev-time call against a broken revision. Need to re-run all 20 cases against the v0.10.4 backend and ship a real PASS rate.

### Doesn't make sense

5. **WIN_PLAN moves vs reality.** Plan locks Moves C/D/E/G as Day 3–8 work and dictates a 12-day demo freeze followed by video + Devpost. We're past Day 4 with none of C/D/E/G shipped — instead v0.10.x ate the week. If the plan is still right, today should be **catch-up day on C/D**; if the plan is wrong, **reframe it** rather than carry stale claims.
6. **"7 agents" vs "5 agents in mesh" in eval `_meta`.** `cases.json` `_meta.agents_in_mesh` lists 5 (`claim_extractor, evidence_grader, vet_rubric, compliance, auditor`). README says 7 agents. The other 2 are `composer` (cert HTML) and `second_opinion` (adversarial post-sign), per `/architecture`. Eval doesn't test them. Inconsistency a judge can catch.
7. **"Vertex AI Search RAG" claim.** Compliance agent is documented to use Vertex AI Search against an FTC §255 + AAFCO + NASC corpus with SHA256 provenance. We should verify that the deployed compliance agent actually queries the corpus on every run (not a hardcoded path), and that `/architecture` link to the corpus index works.
8. **Pricing tiers visible to judges.** The page shows a $499/mo "Pro" tier and "$Custom" Enterprise. Rules don't require pricing be real for the hackathon. But if a judge clicks "Start verifying" or anything ROI-related and we have no signup, that's an empty promise. Either land the buttons somewhere honest (calendly, waitlist), or remove the CTA.

---

## The reframed 15-day plan

The submission needs to optimize for the rubric, not for the buyer hero. Three buckets:

### Bucket 1 — Submission blockers (must be done before Day 17 submit) · 5 items

| # | Item | Effort | Rubric | Owner |
|---|---|---|---|---|
| B0 | **Judge-access checklist on Devpost + README header** — demo API key (`demo-key-2026-06`), curl one-liner, expected response. Audit P0 from codex. | 2 hours | Tech +2, Demo +1 | Omar + Claude |
| B1 | **Flip repo public** + README polish for judge-browsing-code | 1 day | Tech +1, Demo +1 | Omar |
| B2 | **Demo video ≤3 min**, screen-cap of `/` cached demo + Verify + cert + chain head, ElevenLabs founder VO over Lyria bed | 2-3 days | Demo +5–6 | Omar + O22 |
| B3 | **Devpost ~700w text** (problem → why now → buyer → multi-agent → why us → ask) | 1 day | Business +3–4 | Omar |
| B4 | **A2A v0.3 envelope acceptance** — accept both flat `{skill, input}` AND standard `params.message.parts[].text` envelope | 4 hours | Tech +2 | Omar + Claude |

### Bucket 2 — Rubric lift (cut from 5 to 2 after codex review) · 2 items

| # | Item | Effort | Rubric |
|---|---|---|---|
| L1 | **ADK eval re-run** all 20 cases against v0.10.4. Publish real PASS rate. Hide cases that hit non-pet-supplement URLs from the auto-graded total. | 0.5 day | Tech +2 |
| L2 | **Hero cert placeholder fix** — render URN + anchor + signature summary in the hero after cached cycle, not below the fold | 2 hours | Demo +1 |

**Cut from plan (codex 2026-05-21):** L3 A2A inbound traffic log, L4 claim_extractor ADK LlmAgent live runtime, L5 Vertex AI Search corpus query proof. All three are real lift but the 12-day budget can't absorb them with zero buffer. If B0–B4 + L1 + L2 ship by Day 11, we can revisit one of L3/L4/L5 in the polish window.

### Bucket 3 — Polish & dogfooding · do if time

- Hero copy second pass after Devpost is written (the founder voice will sharpen)
- Mobile QA on hero (codex C2 P0-3 mobile call-out)
- Stranger test with 3 fresh readers (Day 15 per WIN_PLAN, still valid)

### Timeline (post-codex reframe)

```
Day 17 (today): B0 judge-access checklist · B4 A2A envelope · L1 ADK eval re-run · L2 hero cert fix
Day 18:         B1 repo public + README polish
Day 19-22:      B2 demo video shoot + edit (4 days; the real bottleneck)
Day 23-24:      B3 Devpost text + stranger test
Day 25:         🔒 DEMO FREEZE (codex final sweep)
Day 26-27:      Absorb stranger test findings · optional L3 revisit if budget allows
Day 28 (06-05): 🚀 SUBMIT by noon PT
```

7 items in 12 days, with a 2-day buffer in Days 26–27. Codex called the prior 12/12 version overpacked; this version preserves submission requirements + the highest-ROI lifts and treats everything else as bonus.

### Projected score after this plan (post-codex cuts)

| Dimension | Today | After this plan | Notes |
|---|---|---|---|
| Technical | 22–24 | 26–28 | B0 + B4 + L1 close the access + spec-compliance + eval gaps |
| Business | 22–24 | 26–28 | B3 Devpost articulation |
| Innovation | 14–16 | 15–17 | No L5 Vertex AI Search proof; rely on Devpost framing alone |
| Demo | 12–14 | 18–20 | B2 video is the big move; L2 + B1 add the polish |
| **Total** | **~70–78** | **~85–93** | Cuts cost ~2 points in Innovation/Tech vs the overpacked plan, in exchange for a real buffer. |

---

## Files where this plan lives

- `docs/SUBMISSION_AUDIT_2026-05-21.md` — this file (the canonical reframe)
- `WIN_PLAN.md` — original 9-move plan (now superseded for Moves C/D/G order)
- `PHASES.md` — phase completion log (still authoritative)
- `tests/adk_eval/` — eval cases + results
- `services/mesh_api/main.py` — A2A endpoint + DID + agent card

---

## Codex handshake — 2026-05-21

**Status: AMENDMENT ABSORBED. Plan ready for execution.**

Codex review verdict: **NEEDS_AMENDMENT → AMENDED**.

Codex flagged one P0 the audit missed and called the original 12-item plan overpacked:

- **P0 (absorbed):** API-key gate (`X-API-Key: demo-key-2026-06`) blocks judges by default; promoted to blocker B0 with explicit Devpost-header treatment.
- **Plan overpack (absorbed):** Original 12/12-day plan had zero buffer. Cut L3 (A2A inbound traffic log), L4 (claim_extractor ADK runtime), L5 (Vertex AI Search corpus proof). Net new shape: 7 items in 10 days + 2-day buffer.

Codex defended the rubric delta (81–88 → 70–78) as honest and called the kept blockers correct. The first code commit should be **B4 (A2A envelope)** paired with **B0 (judge-access checklist)** — these unlock everything else.

Codex final rating: **STRONG (post-amendment)**.

Every Move after this clears codex before the next starts, per CLAUDE.md hard rule 6.
