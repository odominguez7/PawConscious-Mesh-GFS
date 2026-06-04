"""Vet Panel Agent (THIN).

Prompt-encoded 5-vet rubric simulation. No Vertex AI Search, no licensed handbook
ingest. The rubric is derived from public-domain veterinary nutrition principles +
standard clinical claim evaluation patterns.

Production note: in v0.1 this is simulated by Gemini. The roadmap routes
high-stakes claims to a real Boston vet panel (manual attestation). The rubric
simulation here flags those claims for escalation.

Model: gemini-2.5-pro (consistency over speed).
"""
from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from shared.pcec_schema import Claim, ClaimKind, VetRubricScore  # noqa: E402

from google import genai
from google.genai import types
from shared.llm_retry import agenerate


VET_RUBRIC_PROMPT = """You are simulating a panel of 5 board-certified veterinarians (DVM with ACVN or ACVIM specialty) reviewing a pet supplement health claim.

The rubric (each vet scores 1-5):
- 5 = strong RCT evidence in target species, clear mechanism, real clinical magnitude
- 4 = moderate evidence (smaller studies or related species), plausible mechanism
- 3 = mixed or limited evidence, mechanism plausible but not proven
- 2 = sparse evidence, weak mechanism, mostly extrapolation
- 1 = no peer-reviewed evidence supporting the claim direction; promotional language

After all 5 vets score, return:
- The average score (rounded to nearest integer 1-5)
- A 1-2 sentence rationale citing the dominant pattern
- escalate_to_human_vet: true if score ≤ 3 OR if the claim involves clinical disease management (e.g., 'treats arthritis', 'prevents infection'); false otherwise

Be HONEST. If the claim is unsubstantiated puffery ('the best for your dog'), score 1. If it's well-grounded ('contains chondroitin which has 4 supporting RCTs in canine osteoarthritis'), score 4-5.

Claim: "{claim_text}"
Claim kind: {claim_kind}
Context on PDP: "{claim_context}"

Return ONLY valid JSON: {{
  "score": <int 1-5>,
  "rationale": "...",
  "escalate_to_human_vet": <true|false>
}}
"""


def _client() -> genai.Client:
    return genai.Client(vertexai=True, project="pawconscious-mesh-2026", location="us-central1")


async def score_claim(claim: Claim) -> VetRubricScore:
    """Run the 5-vet rubric simulation on one claim."""
    client = _client()
    prompt = VET_RUBRIC_PROMPT.format(
        claim_text=claim.text,
        claim_kind=claim.kind.value,
        claim_context=claim.raw_context or "(no surrounding context)",
    )
    response = await agenerate(client, 
        model="gemini-2.5-pro",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.0,
        ),
    )
    payload = json.loads(response.text)
    score = int(payload.get("score", 3))
    score = max(1, min(5, score))  # clamp
    return VetRubricScore(
        claim=claim,
        score=score,
        rationale=str(payload.get("rationale", "")),
        escalate_to_human_vet=bool(payload.get("escalate_to_human_vet", False)),
    )


async def main() -> None:
    """Verification: score a few real Native Pet claims."""
    test_claims = [
        Claim(
            text="Supports joint health and mobility",
            kind=ClaimKind.EFFICACY,
            raw_context="Nutrients like chondroitin (found in green lipped mussels) and ingredients like turmeric reduce inflammation, boost joint health, and support your pup's cartilage.",
        ),
        Claim(
            text="A blend of powerful polyphenols helps to keep your dog fit and active while supporting normal blood pressure and supporting your dog's cardiovascular health.",
            kind=ClaimKind.EFFICACY,
            raw_context="Relief from Daily Activity. A blend of powerful polyphenols...",
        ),
        Claim(
            text="Dogs think it's a treat!",
            kind=ClaimKind.PERFORMANCE,
            raw_context="why dogs love it. Savory chicken chews with a jerky-style texture. Dogs think it's a treat!",
        ),
    ]

    for claim in test_claims:
        result = await score_claim(claim)
        print(f"\nClaim: {claim.text!r}")
        print(f"Score: {result.score}/5 | Escalate: {result.escalate_to_human_vet}")
        print(f"Rationale: {result.rationale}")


if __name__ == "__main__":
    asyncio.run(main())
