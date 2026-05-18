# Run PawConscious Mesh in 3 commands

Judge-ready reproducibility per codex G9 #7.

## Prerequisites

- Python 3.11+ (tested with 3.14.5)
- `gcloud` CLI installed + authenticated
- Access to GCP project `pawconscious-mesh-2026` (or your own with required APIs)
- Application Default Credentials configured for Vertex AI

## Environment variables

```bash
export GOOGLE_CLOUD_PROJECT=pawconscious-mesh-2026
export GOOGLE_CLOUD_LOCATION=us-central1
export GOOGLE_GENAI_USE_VERTEXAI=true
```

Optional (if running outside the active gcloud config):
```bash
gcloud auth application-default login
gcloud auth application-default set-quota-project pawconscious-mesh-2026
```

## The 3 commands

```bash
# 1. Setup
git clone https://github.com/odominguez7/PawConscious-Mesh-GFS && cd PawConscious-Mesh-GFS
python3 -m venv .venv && source .venv/bin/activate
pip install -e .

# 2. Run claim extraction against a real pet supplement PDP
python agents/claim_extractor.py
# Returns 30-50 real claims extracted from Native Pet Hip+Joint product page

# 3. Run evidence grading on one extracted claim
python agents/evidence_grader.py
# Returns real PubMed PMIDs with relevance scores + claim-direction support
```

## Expected output

`claim_extractor.py`:
```
Fetching: https://www.nativepet.com/products/hip-joint

Extracted 42 claims:

1. [efficacy] Hip+Joint Inflammatory Care
   position: hero
   context: ...
2. [efficacy] Supports joint health and mobility
   ...
```

`evidence_grader.py`:
```
Grading claim: 'Supports joint health and mobility'

Returned 4 graded papers:

1. PMID 40685570 | relevance 1.00 | supports
   This review on feline osteoarthritis highlights a study where a therapeutic diet with omega-3s, turmeric, and collagen was as effective as standard drugs...
2. PMID 32316397 | relevance 1.00 | supports
   ...
```

## What you're verifying

- **Claim extractor** uses Gemini 2.5 Pro on Vertex AI to extract every health claim from a product page, classify each by kind (efficacy/safety/ingredient/expert/provenance/performance), and capture its position + context. No fabrication — only claims present in the page text.
- **Evidence grader** uses Gemini to extract PubMed-suitable search terms, queries PubMed via BioMCP (10k+ char real markdown response with real PMIDs), then uses Gemini again to grade each result's relevance to the claim and whether it supports the claim direction.
- Both agents return Pydantic-validated objects per the PCEC v0.1 schema in `shared/pcec_schema.py`.

## What's NOT in this command set (build pipeline)

- The 3 thin agents (vet-panel, compliance, auditor) — Phase 3, in progress
- The orchestrator (ParallelAgent fan-out + SequentialAgent merge) — Phase 3
- The public A2A v0.3 agent card endpoint — Phase 4
- The ShopperAgent external consumer — Phase 4
- Cloud Run deployment + public hosted URL — Phase 5

See `PLAN.md` for the full 18-day build.

## Known limitations (honest)

- **MCP protocol layer:** v0.1 calls BioMCP via direct Python lib import (the `biomcp-python` package). Per codex G9 P0, full MCP protocol compliance requires running `biomcp serve` and calling via MCP client. Phase 2.5 refactor scheduled.
- **AI2 Asta citation grading:** deferred to Phase 2.5 (cite-count + influential-cite-count currently 0/0).
- **Vet attestation + signing:** Phase 3-4.
- **Continuous monitoring + cert TTL:** Phase 4-5.

## Cost expectations

Per claim extraction: ~$0.01 (single Gemini 2.5 Pro call).
Per evidence grading (with PubMed search): ~$0.05 (3 Gemini calls + free BioMCP query).

Full hackathon-period spend estimate: under $50 across Vertex AI + Cloud Run.
