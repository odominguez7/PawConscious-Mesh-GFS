"""PCEC v0.1 Pydantic schemas for the agent pipeline.

Draft proposal — not a standard. Single operator (PawConscious) v0.1.
See docs/PCEC-v0.md for the full schema specification.
"""
import json
from datetime import datetime
from enum import Enum
from typing import Optional, Any
from pydantic import BaseModel, Field


def canonical_bundle_bytes(obj: Any) -> bytes:
    """Transport-stable canonical bytes for hashing + signing a bundle.

    The bytes any party (server OR an external verifier) can reproduce from the
    bundle alone: JSON-mode primitives (datetimes -> ISO strings, enums ->
    values), keys sorted, compact separators.

    Two fields are excluded because they are NOT signed content:
    - `signature` — the signature can't sign itself.
    - `bundle_urn` — it is derived from bundle_hash (urn_for_hash) and is set
      AFTER hashing/signing, so it must be excluded or the signed bytes (urn
      absent) won't match the served bytes (urn populated). A verifier can
      recompute it from the hash.

    Critically, this is reproducible from the *served* bundle dict — unlike
    Pydantic's `model_dump_json` (field-definition order, not transport-stable),
    which a client cannot reconstruct after a JSON round-trip. Accepts either an
    EndorsementClaimBundle (uses model_dump) or a plain dict (a received bundle).
    """
    d = obj.model_dump(mode="json") if hasattr(obj, "model_dump") else dict(obj)
    d.pop("signature", None)
    d.pop("bundle_urn", None)
    # Number canonicalization (toward RFC 8785): a whole-valued float must
    # serialize identically in every language. Python json emits 1.0, but
    # JavaScript JSON.stringify emits 1 (it can't tell a whole float from an
    # int after JSON.parse). Collapse whole floats to ints so a browser
    # verifier reproduces the exact bytes. bool is not a float, so it's safe.
    def _nums(x):
        if isinstance(x, float):
            return int(x) if x.is_integer() else x
        if isinstance(x, dict):
            return {k: _nums(v) for k, v in x.items()}
        if isinstance(x, list):
            return [_nums(v) for v in x]
        return x
    d = _nums(d)
    return json.dumps(d, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


class ClaimKind(str, Enum):
    EFFICACY = "efficacy"
    SAFETY = "safety"
    INGREDIENT = "ingredient"
    EXPERT = "expert"
    PROVENANCE = "provenance"
    PERFORMANCE = "performance"


class Claim(BaseModel):
    """One extracted product claim from a PDP."""
    text: str = Field(..., description="The exact claim copy")
    kind: ClaimKind = Field(..., description="Claim category")
    position_on_page: Optional[str] = Field(None, description="Where on the PDP")
    raw_context: Optional[str] = Field(None, description="Surrounding copy for disambiguation")


class Evidence(BaseModel):
    """One PubMed paper supporting (or contradicting) a claim."""
    pmid: str = Field(..., description="PubMed ID")
    doi: Optional[str] = None
    title: Optional[str] = None
    relevance_score: float = Field(..., ge=0.0, le=1.0)
    citation_count: int = Field(default=0, ge=0)
    influential_citation_count: int = Field(default=0, ge=0)
    supports_claim_direction: bool = Field(default=True)
    notes: Optional[str] = None


class EvidenceBundle(BaseModel):
    claim: Claim
    papers: list[Evidence] = Field(default_factory=list)
    grader_agent: str = "did:web:mesh-api-40952019806.us-central1.run.app:agents:evidence-grader"
    grader_run_id: Optional[str] = None


class VetRubricScore(BaseModel):
    claim: Claim
    score: int = Field(..., ge=1, le=5, description="5-vet rubric average")
    rationale: str
    escalate_to_human_vet: bool = False


class GroundingSource(BaseModel):
    """Per codex G14 #7 — grounding provenance for traceability."""
    source_id: str = Field(..., description="Document ID from Vertex AI Search")
    snippet: str = Field(..., description="Retrieved passage text")
    snippet_hash: str = Field(..., description="sha256 of snippet for tamper-evidence")


class ComplianceMapping(BaseModel):
    claim: Claim
    ftc_section: Optional[str] = Field(None, description="e.g., '16 CFR §255.3'")
    aafco_definition: Optional[str] = None
    nasc_public_standard: Optional[str] = None
    violation_flag: bool = False
    rationale: str
    grounding_sources: list[GroundingSource] = Field(
        default_factory=list,
        description="Provenance per codex G14 — Vertex AI Search retrieval results that grounded this mapping",
    )


class AuditVerdict(BaseModel):
    """Adversarial pass — citation existence + claim-direction match."""
    claim: Claim
    verdict: str = Field(..., description="PASS / FAIL / CONDITIONAL")
    challenges_run: list[str] = Field(default_factory=list)
    findings: list[str] = Field(default_factory=list)
    auditor_agent: str = "did:web:mesh-api-40952019806.us-central1.run.app:agents:auditor"


class EndorsementClaimBundle(BaseModel):
    """The full signed bundle returned to the brand."""
    sku: str
    product_url: str
    claims: list[Claim]
    evidence: list[EvidenceBundle]
    vet_scores: list[VetRubricScore]
    compliance: list[ComplianceMapping]
    audit: list[AuditVerdict]
    issued_at: datetime = Field(default_factory=datetime.utcnow)
    issuer: str = "did:web:mesh-api-40952019806.us-central1.run.app"
    bundle_urn: Optional[str] = None
    signature: Optional[str] = None
