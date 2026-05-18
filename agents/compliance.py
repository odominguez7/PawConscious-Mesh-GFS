"""Compliance Agent (THIN per PLAN.md §2 — codex G7 P0.7 + G7.2).

Maps each claim to public-redistributable regulator/standard language:
- FTC 16 CFR §255 (Endorsement Guides, 2023 update — federal text, public domain)
- AAFCO Model Regulations PF7 + PF9 (public-side ingredient definitions)
- NASC Quality Seal program public-side substantiation requirements

NO licensed handbook ingest (codex G7 P0.7 explicit). v0.1 ships with prompt-only;
Vertex AI Search corpus ingest is Phase 5 work.

Model: gemini-2.5-pro.
"""
from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

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


def _client() -> genai.Client:
    return genai.Client(vertexai=True, project="pawconscious-mesh-2026", location="us-central1")


async def map_claim(claim: Claim) -> ComplianceMapping:
    """Map one claim to FTC/AAFCO/NASC standards."""
    client = _client()
    prompt = COMPLIANCE_PROMPT.format(
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
