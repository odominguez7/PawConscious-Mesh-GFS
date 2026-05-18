"""Compliance Agent (GROUNDED via Vertex AI Search per codex G13 Phase 8).

Maps each claim to public-redistributable regulator/standard language using
Vertex AI Search RAG over a corpus of:
- FTC 16 CFR §255.0, .1, .2, .3, .5 (Endorsement Guides, 2023 update)
- AAFCO PF7 Substantiation of Claims (public summary)
- NASC Quality Seal program public-side requirements

NO licensed handbook ingest (codex G7 P0.7). All sources public-redistributable.
Data store: projects/40952019806/locations/global/.../acp-regulator-corpus

Model: gemini-2.5-pro with vertex_ai_search retrieval grounding.
"""
from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from shared.pcec_schema import Claim, ClaimKind, ComplianceMapping  # noqa: E402

from google import genai
from google.genai import types


COMPLIANCE_PROMPT = """You are the compliance agent in the PawConscious Mesh / ACP system.

Map this pet supplement claim to the relevant US regulator / standards language. Use ONLY the following public-domain or public-side sources:

1. **FTC 16 CFR §255 (Endorsement Guides, 2023 update).**
   - §255.3 Expert Endorsements: an expert endorser must hold the credentials implied, AND must have actually exercised that expertise (testing/examination at least as extensive as similar expertise normally requires).
   - §255.2 Consumer Endorsements: typicality required; explicit substantiation expected; testimonial == endorsement.
   - §255.1 General: endorsements must reflect honest opinions, findings, and experience of the endorser; deceptive endorsements are prohibited; substantiation in the advertiser's possession sufficient to support the claims.

2. **AAFCO Model Regulations (PF7 Substantiation of Claims).**
   - PF7 requires claims to be substantiated with scientifically valid evidence.
   - 'Vet-recommended' = requires statistically significant, professionally sound survey of vets.
   - 'Vet-formulated' = requires at least one documented vet involved in formulation.

3. **NASC Quality Seal (public-side requirements).**
   - Biennial independent third-party audit.
   - Written SOPs.
   - Adverse Event Reporting (AER) system.
   - Labeling compliance.
   - Random product testing for label accuracy (NOT clinical efficacy).
   - NASC does NOT certify clinical efficacy claims.

Claim: "{claim_text}"
Claim kind: {claim_kind}
Context: "{claim_context}"

For this claim, return JSON with:
- ftc_section: which §255 subsection (or 'none' if not applicable)
- aafco_definition: which AAFCO definition applies (or 'none')
- nasc_public_standard: which NASC public-side requirement applies (or 'none')
- violation_flag: true if the claim as written would likely fail substantiation under §255, NOT true otherwise
- rationale: 1-2 sentences explaining the mapping

Be HONEST. If the claim is well-substantiated puffery that doesn't trigger any rule (e.g., 'real chicken base'), mark all 'none' + violation_flag false. If it's clinical disease language ('treats arthritis'), flag a §255 violation absent supporting evidence.

Return ONLY valid JSON, no markdown.
"""


VERTEX_SEARCH_PROJECT = "40952019806"
VERTEX_SEARCH_LOCATION = "global"
VERTEX_SEARCH_DATA_STORE = "acp-regulator-corpus"


def _client() -> genai.Client:
    return genai.Client(vertexai=True, project="pawconscious-mesh-2026", location="us-central1")


def _search_data_store_path() -> str:
    return (
        f"projects/{VERTEX_SEARCH_PROJECT}/locations/{VERTEX_SEARCH_LOCATION}/"
        f"collections/default_collection/dataStores/{VERTEX_SEARCH_DATA_STORE}/"
        f"servingConfigs/default_serving_config"
    )


async def retrieve_grounding_passages(claim: Claim, max_results: int = 3) -> list[str]:
    """Direct Vertex AI Search retrieval — returns top-K passages with citations.

    Manual-retrieval pattern because Gemini's vertex_ai_search Tool is incompatible
    with response_mime_type='application/json' (controlled generation). We call
    Search directly, inject passages into the prompt, then Gemini with JSON mode.
    """
    try:
        from google.cloud import discoveryengine
        from google.api_core.client_options import ClientOptions

        client_options = ClientOptions(api_endpoint="discoveryengine.googleapis.com")
        client = discoveryengine.SearchServiceClient(client_options=client_options)

        # Build query from claim text + kind for better retrieval
        query = f"{claim.text} {claim.kind.value} endorsement substantiation"

        request = discoveryengine.SearchRequest(
            serving_config=_search_data_store_path(),
            query=query,
            page_size=max_results,
        )
        response = client.search(request=request)
        passages: list[str] = []
        for result in response.results:
            doc = result.document
            # Extract derivedStructData snippets (the retrieved passage text)
            derived = doc.derived_struct_data or {}
            snippets = derived.get("snippets", [])
            for s in snippets[:1]:  # top snippet per doc
                snippet_text = s.get("snippet", "")
                if snippet_text:
                    doc_id = doc.id or doc.name.split("/")[-1]
                    passages.append(f"[Source: {doc_id}]\n{snippet_text}")
        return passages
    except Exception as e:
        print(f"[compliance] retrieval failed: {e}")
        return []


async def map_claim(claim: Claim) -> ComplianceMapping:
    """Map one claim to FTC/AAFCO/NASC standards with manual Vertex AI Search grounding."""
    # Step 1: retrieve grounding passages from the regulator corpus
    passages = await retrieve_grounding_passages(claim)
    grounding_block = (
        "GROUNDED REGULATORY PASSAGES (from Vertex AI Search over public corpus):\n---\n"
        + "\n\n".join(passages) + "\n---\n"
    ) if passages else "(grounding unavailable — using prompt-only knowledge)\n"

    # Step 2: Gemini call with JSON mode + grounded passages in prompt
    client = _client()
    prompt = grounding_block + "\n" + COMPLIANCE_PROMPT.format(
        claim_text=claim.text,
        claim_kind=claim.kind.value,
        claim_context=claim.raw_context or "(no surrounding context)",
    )
    response = client.models.generate_content(
        model="gemini-2.5-pro",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.0,
        ),
    )
    payload = json.loads(response.text)

    return ComplianceMapping(
        claim=claim,
        ftc_section=payload.get("ftc_section") if payload.get("ftc_section") != "none" else None,
        aafco_definition=payload.get("aafco_definition") if payload.get("aafco_definition") != "none" else None,
        nasc_public_standard=payload.get("nasc_public_standard") if payload.get("nasc_public_standard") != "none" else None,
        violation_flag=bool(payload.get("violation_flag", False)),
        rationale=str(payload.get("rationale", "")),
    )


async def main() -> None:
    test_claims = [
        Claim(
            text="Veterinarian formulated",
            kind=ClaimKind.EXPERT,
            raw_context="Trusted by 10,000+ veterinarians and pet parents nationwide.",
        ),
        Claim(
            text="Supports joint health and mobility",
            kind=ClaimKind.EFFICACY,
            raw_context="Nutrients like chondroitin and turmeric reduce inflammation.",
        ),
        Claim(
            text="The best supplement for your dog",
            kind=ClaimKind.PERFORMANCE,
            raw_context="Promotional headline.",
        ),
    ]

    for claim in test_claims:
        result = await map_claim(claim)
        print(f"\nClaim: {claim.text!r}")
        print(f"FTC: {result.ftc_section} | AAFCO: {result.aafco_definition} | NASC: {result.nasc_public_standard}")
        print(f"Violation: {result.violation_flag}")
        print(f"Rationale: {result.rationale}")


if __name__ == "__main__":
    asyncio.run(main())
