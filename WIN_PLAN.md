# WIN_PLAN — PawConscious-GFS · GFS AI Agents Challenge Track 3
**Locked 2026-05-19 night · Day 1 of 17 to 2026-06-05 5 PM PT submit deadline**

This is the live canonical plan. Updated per move as work ships.

## Where we are right now

Live: https://mesh-api-40952019806.us-central1.run.app/ (revision being deployed = v0.4.0-biz)
Repo: https://github.com/odominguez7/PawConscious-Mesh-GFS (still private)
Day 1 ships: 13 commits · 4 codex handshakes cleared · cached agent demo + Business Case block + E2E verified.

| Rubric (verbatim from Devpost) | Weight | Today | Ceiling |
|---|---|---|---|
| Technical Implementation | 30% | 26-28 | 30 |
| Business Case | 30% | 22-24 (post Move B) | 30 |
| Innovation & Creativity | 20% | 16-17 | 20 |
| Demo & Presentation | 20% | 17-19 | 20 |
| **Total** | **100%** | **~81-88** | **100** |

Track 3 hard mandates ✅ all 4 met. Key Considerations ✅ all 5 met. Mandatory tech ✅ all 3 present.

## The 9 moves to 100/100

| Day | Move | Status | What | Rubric lift |
|---|---|---|---|---|
| 1 | (Stages 0/1/2A/2A.1/v0.3.x) | ✅ shipped | Truth-up · feature flag · deck-aligned shell · cached demo · E2E shape fix | foundation |
| 2 | **A** flip v2 default | ✅ shipped (8db978b) | `/` serves v2; `/?v=v1` fallback | Demo +1 |
| 2 | **B** Business Case block | ✅ shipped (8db978b) | Buyer/ROI/pricing/procurement on live | Business +5-6 |
| 3 | **C** Stage 2.5 truth hardening | pending | Cert label honesty + chain anchor truth + empty-URL error | credibility |
| 3-4 | **D** Stage 3 A2A round-trip | pending | Fix ShopperAgent polling OR fallback to live A2A traffic log | Tech +3-4 |
| 5 | **E** ADK eval baseline | pending | 20-30 eval cases on real PDPs, PASS/FAIL badge on README | Tech +1-2 |
| 6 | **F** `/architecture` route | pending | Clean SVG export with all 4 mandates labeled. Required artifact | Demo +1-2 |
| 7-8 | **G** UX polish + responsive | pending | Verdict-logic consistency fix + mobile QA + second typography pass | Demo +1 |
| 9-10 | **H** Repo public + content | pending | Flip GitHub public + README/ARCHITECTURE polish for judges browsing code | Tech +1, Demo +1 |
| 11 | Buffer + final codex sweep | pending | Full submission-package adversarial review | catches any P0 |
| **12** | 🔒 **DEMO FREEZE** | scheduled | No more live changes (codex C2 P0-3) | — |
| 13-14 | **I** Video ≤3min | pending | Screen-cap of `/` cached demo → Verify → cert → chain head + ElevenLabs founder VO | Demo +5-6 |
| 14-15 | **J** Devpost text | pending | ~700w problem → why now → buyer → multi-agent → why us → ask | Business +3-4 |
| 15 | Stranger test | pending | 3 fresh readers grade Devpost + live URL + video | catches blind spots |
| 16 | Absorb stranger-test P1s | pending | — | — |
| **17** | 🚀 **SUBMIT by noon PT** | scheduled | 5hr buffer to 5PM PT deadline | — |

## What 100/100 requires per each rubric line (verbatim)

**Technical Implementation 30%** — code quality + use of mandatory tech (Gemini + ADK + Cloud Run) + Key Considerations (Agent Engine ✅ + Vertex AI Search grounding ✅ + multi-agent collaboration via A2A ✅) + Track 3 hard mandates (B2B + Cloud Run + Gemini + A2A all ✅). Gap-closers: A2A round-trip (Move D) + ADK eval badge (Move E) + repo public for code review (Move H).

**Business Case 30%** — per the rule's only specification ("Clearly articulate a compelling business use case for your multi-agent solution"). Articulation, not external proof. Moves B (live page) + J (Devpost text) max this. No LOIs/quotes required by rules.

**Innovation & Creativity 20%** — rules don't sub-specify. Differentiators in repo: PCEC v0.1 open spec · cryptographic chain anchor · A2A trust mesh framing · Falsifier auditor. Move J Devpost text names all 4 explicitly.

**Demo & Presentation 20%** — required artifacts: Video + Architecture diagram + Testing access link. Moves F + G + I produce all three.

## What's EXPLICITLY out of scope (not in rules)

Cloud Marketplace partner application · Gemini Enterprise tenant registration · Model Armor · external validation outreach (LOIs/quotes) · PCEC coalition founding members · Standalone `pcec-spec` repo · AgentOps · Agent Registry registration · Veo cinematic plates · corpus expansion · Firestore task store · ALL labeled aspirational by codex C1 and rule-text audit (commit `97f7cbe`, memory `feedback-no-inferred-hackathon-requirements`).

If you want any of these added back as polish, say so. They don't move rubric points per the rules, but they may move taste.

## Projected score

**92-98/100.** A genuine 100 is unrealistic on a curve, but:
- **Best of Track 3** ($10K cash + $7.5K credits) is the realistic prize at this trajectory
- **Overall Grand Prize** ($15K cash + $10K credits) is the stretch goal

## Files where the plan lives

- `WIN_PLAN.md` — this file, current canonical, lives in repo
- `HANDOFF_2026-05-19.md` — Day 1 end-of-day handoff for resume
- `~/.gstack/projects/odominguez7-PawConscious-Mesh-GFS/ceo-plans/2026-05-19-pawconscious-vision-aligned-10of10-plan.md` — original 7-stage CEO plan with codex C1+C2 amendments (local, not in repo)
- Memory entries (auto-loaded next session): `project-pawconscious-gfs-10of10-plan` · `project-pawconscious-gfs-s2a-shipped` · `project-pawconscious-gfs-v030-design` · `project-pawconscious-gfs-day1-complete`
- `PLAN.md` — original 19-day roadmap from session zero (now superseded by this doc)

## Codex handshake protocol (locked rule)

Every move ships → codex challenge → P0 blocks next move → P1 amendments absorbed before progression. History today:
- C1 (live product audit): 3 P0 + 12 P1 + 2 P2 → absorbed
- C2 (this plan): DO NOT SHIP without 3 changes → all absorbed
- S0+S1: CLEAR with doc-drift P1 → absorbed
- S2A: DO NOT FLIP (hero collision + unsourced claims) → absorbed
- S2B-design: FIX FIRST (API key + response shape P0s) → absorbed
- S2C: pending — runs after v0.4.0 deploys
