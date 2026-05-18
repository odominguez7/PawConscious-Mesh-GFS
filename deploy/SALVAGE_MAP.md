# GUARDIAN → PawConscious Mesh salvage map

**Status:** REFERENCE ONLY. Files inventoried, not yet ported. Port happens in Phase 2 + Phase 3 + Phase 4 after each codex phase-handshake clears.

**Source:** `~/Desktop/GFS - guardIAn/` (GUARDIAN GCP project billing UNLINKED; code preserved on `odominguez7/guardian` GitHub public + local working tree)

**Target:** `~/Desktop/PawConscious-GFS/agents/` and `~/Desktop/PawConscious-GFS/services/`

---

## High-value salvage candidates

| Source file | Lines | Destination | Use in PawConscious Mesh | Phase |
|---|---|---|---|---|
| `app/agents/falsifier.py` | TBD | `agents/auditor.py` | Adversarial pass on merged claim bundle (citation-existence + claim-direction). Per codex G7.3 P1.6, downgraded to simple consistency check (not full ADK Eval) | Phase 3 |
| `app/tools/falsifier.py` | TBD | `agents/auditor_tools.py` | Falsifier helper functions | Phase 3 |
| `app/tools/a2a_peers.py` | TBD | `services/mesh_api/a2a_endpoint.py` | A2A v0.3 client + agent card publisher. Adapt for /.well-known/agent-card.json + verify_claim skill | Phase 4 |
| `app/tools/board_slide.py` | TBD | `services/mesh_api/cert_renderer.py` | Cert + draft-evidence PDF renderer (the GUARDIAN board-slide html2canvas + LRU cache patterns) | Phase 4 |
| `tests/unit/test_falsifier.py` | TBD | `tests/test_auditor.py` | Reference test patterns; adapt for vet-rubric-aware consistency check | Phase 3 |
| `tests/integration/test_a2a_*.py` | TBD | `tests/test_a2a_endpoint.py` | A2A integration test patterns | Phase 4 |
| `ops-center/` (Next.js project tree) | TBD | `services/mesh_api/portal/` | Mesh Console UI (Hero + Live Mesh + Audit Trail tabs); the v3.2 3-tab architecture port | Phase 4 |
| `marketplace/PROCUREMENT.md` | TBD | `docs/marketplace/PROCUREMENT.md` | SOC2 roadmap + DPA + SLA + MSA + SIG questionnaire pre-filled (adapt for ACP) | Phase 6 if time |
| `marketplace/LISTING.md` | TBD | `docs/marketplace/LISTING.md` | Marketplace listing copy (adapt for ACP) | Phase 6 if time |
| `marketplace/DEVPOST_SUBMISSION.md` | TBD | `docs/devpost-submission.md` | Devpost copy template (heavily adapt) | Phase 7 (post-overnight) |

## NOT salvaging (intentional)

- All wildlife / NPS / SDZWA cam code — dead direction
- `species_id` + `stream_watcher` + `audio_agent` — wildlife-specific
- `mission_bridge` Imagen 4 portraits — wildlife-themed
- 3D Mapbox terrain code — irrelevant
- ElevenLabs voice config files — generic, port only if needed for demo VO
- Veo wildlife render scripts — different prompt set needed
- All `reviews/v9-*` files except the CEO-pivot draft (already informed PawConscious Mesh planning)

## Port discipline

1. NEVER copy-paste blindly. Read source file → understand intent → re-write idiomatic ADK 2.0 for new codebase
2. Stripped GUARDIAN-specific naming (`guardian-*`, `park-*`, `cam-*`) → ACP-namespaced (`acp-*`, `claim-*`, `pet-*`)
3. Every ported function gets a one-line docstring noting source provenance
4. Tests adapted not copied — pet-vertical fixtures replace wildlife fixtures
5. Per `feedback_no_fake_things`: if a salvaged function depends on wildlife-specific infra (NPS API, Camzone HLS), strip the dep entirely; don't carry dead code

## Order of port operations

Per phase-handshake rule, salvage happens INSIDE the phase build, not before:

- **Phase 2:** none (claim-extractor + evidence-grader are net-new)
- **Phase 3:** port Falsifier → Auditor (consistency check variant only, per codex G7.3)
- **Phase 4:** port A2A peer scaffold → A2A endpoint + agent card; port board_slide → cert renderer; port Ops Center 3-tab UI → Mesh Console
- **Phase 5:** port Cloud Run deploy scripts + Dockerfile patterns
- **Phase 6:** port marketplace docs if time permits

All ports get committed individually with "salvage: <file> from GUARDIAN" prefix so the lineage is traceable in git history.
