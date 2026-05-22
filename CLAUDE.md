# CLAUDE.md: PawConscious Mesh

## Project context
PawConscious Mesh is the GFS AI Agents Challenge submission (deadline 2026-06-05). Port of GUARDIAN's agentic A2A architecture onto the PawConscious commercial wedge. Read `PLAN.md` first for the validated strategy and 19-day roadmap.

## Taste rule-book (read first every session)
See [`docs/TASTE.md`](docs/TASTE.md) for twelve rules earned in shipped commits, sourced from Sarah Tavel's "Taste" essay. Every code, copy, visual, or surface decision tests against these rules in the application order at the bottom of that doc. The taste rule-book takes precedence over inferred best-practice when they disagree.

## Hard rules (from Omar's repo + user-level instructions)

1. **No fake things.** If a feature doesn't work, fix it or remove it. Never hide broken buttons, never mock the integration the demo points at, never stub the agent and claim it's real. (`feedback_no_fake_things`)
2. **Verify in browser before claiming done.** UI changes require opening the live URL and screenshotting. Backend payload right ≠ user seeing it right. (`feedback_verify_in_browser`)
3. **Audit repo before claiming state.** Filesystem + git log + .env + working tree + rendered artifacts BEFORE narrative claims. Reviews/PLAN.md/memory lag the code. (`feedback_audit_repo_not_narrative`)
4. **Source every number.** Never quote odds/% without a reference base. All market sizing claims cite inline. (`feedback_no_unsourced_probabilities`)
5. **Writing style.** No em dashes. No "thrilled". MIT founder language. (`feedback_writing_style`)
6. **Codex handshake per Move.** Every Move clears codex before the next Move starts. P0 findings block. Amendments absorbed. (`feedback_codex_handshake_per_move`, `feedback_codex_velocity`)
7. **Save memory per Move.** After codex CLEAR. Browser-disconnects + session resets are why. (`feedback_save_memory_per_move`)
8. **Env files are sacred.** Never `cat > .env.local <<EOF` for a single key. Read first, Edit one key. Nukes other secrets. (`feedback_env_local_overwrites`)
9. **gcloud configs are per-project.** Run project's runbook before any gcloud cmd. Never `gcloud config set project` on shared config. (`feedback_gcloud_per_project_configs`)
10. **Autonomous execution.** When Omar says "do all you can autonomously," ship code/files/commits not plans. (`feedback_autonomous_execution`)
11. **Plain human language.** No clinical/medical jargon in user-facing copy. (`feedback_no_clinical_jargon`)
12. **Science + reader psychology, not opinion.** Justify copy/design choices with evidence. (`feedback_science_reader`)

## Skill routing
- Product ideas / brainstorming → invoke /office-hours
- Strategy / scope → invoke /plan-ceo-review
- Architecture → invoke /plan-eng-review
- Design system / plan review → invoke /plan-design-review
- Full review pipeline → invoke /autoplan
- Bugs / errors → invoke /investigate
- QA / testing site behavior → invoke /qa
- Code review / diff check → invoke /review
- Visual polish → invoke /design-review
- Ship / deploy / PR → invoke /ship or /land-and-deploy
- Save progress → invoke /context-save
- Resume context → invoke /context-restore

## Stack
- ADK 2.0 + Vertex AI Agent Engine + Gemini 3 Pro / 2.5 Flash
- A2A v0.3 (Linux Foundation)
- BioMCP + AI2 Asta MCP + Firecrawl MCP + Gemini grounding (NO Natoma)
- Cloud Run (per agent), Firestore (state + transparency log), Cloud SQL (cert registry), BigQuery (analytics)
- Vertex AI Search (vet + regulator corpora)
- Next.js portal frontend, Mesh Console UI
- O22 pipeline (Veo 3.1 + Lyria 2 + ElevenLabs) for demo render
- MIT license, public repo

## GCP
- Active project: `pawconscious-mesh-2026` (to be created in Phase 1)
- Billing account: `014E26-090236-16FFE3`
- gcloud config name: `pawconscious-mesh` (to be created)
- `guardian-gfs-2026` billing was UNLINKED 2026-05-17 night per Omar's call. Resources preserved, no spend. Re-link with: `gcloud beta billing projects link guardian-gfs-2026 --billing-account=014E26-090236-16FFE3`

## Repo provenance
- Salvage from `~/Desktop/GFS - guardIAn/` (GUARDIAN v9 latest commit `69329a4`)
- Salvage from `~/Desktop/PawConscious/` (live PawConscious site)
- Salvage from O22 pipeline (cinematic demo renderer)
- New work: ADK migration, A2A public card, PCEC v0.1 spec, BioMCP + Asta integration, signed VCs, transparency log

## Submission requirements (GFS AI Agents Challenge)
- Public hosted URL (web, iOS, or Android)
- Public open-source repo (OSI-approved license, visible at top)
- Demo video ≤3 min, English or English-subtitled, YouTube/Vimeo public
- Text description (feature, tech, data sources, findings)
- Built on Google Cloud (Gemini + Agent Builder + Partner MCP)
- Newly created during contest period (May 5 – Jun 11, 2026 for Rapid Agent; verify for GFS Agents Challenge)
- All team members listed as project members on Devpost

## GBrain Search Guidance (configured by /sync-gbrain)
<!-- gstack-gbrain-search-guidance:start -->

GBrain is set up and synced on this machine. The agent should prefer gbrain
over Grep when the question is semantic or when you don't know the exact
identifier yet.

**This worktree is pinned to a worktree-scoped code source** via the
`.gbrain-source` file in the repo root (kubectl-style context). Any
`gbrain code-def`, `code-refs`, `code-callers`, `code-callees`, or `query`
call from anywhere under this worktree routes to that source by default
(no `--source` flag needed). Conductor sibling worktrees of the same repo
each have their own pin and their own indexed pages, so semantic results
match the actual code on disk in this worktree.

Two indexed corpora available via the `gbrain` CLI:
- This worktree's code (auto-pinned via `.gbrain-source`).
- `~/.gstack/` curated memory (registered as `gstack-brain-<user>` source via
  the existing federation pipeline).

Prefer gbrain when:
- "Where is X handled?" / semantic intent, no exact string yet:
    `gbrain search "<terms>"` or `gbrain query "<question>"`
- "Where is symbol Y defined?" / symbol-based code questions:
    `gbrain code-def <symbol>` or `gbrain code-refs <symbol>`
- "What calls Y?" / "What does Y depend on?":
    `gbrain code-callers <symbol>` / `gbrain code-callees <symbol>`
- "What did we decide last time?" / past plans, retros, learnings:
    `gbrain search "<terms>" --source gstack-brain-<user>`

Grep is still right for known exact strings, regex, multiline patterns, and
file globs. Run `/sync-gbrain` after meaningful code changes; for ongoing
auto-sync across all worktrees, run `gbrain autopilot --install` once per
machine. gbrain's daemon handles incremental refresh on a schedule.

<!-- gstack-gbrain-search-guidance:end -->
