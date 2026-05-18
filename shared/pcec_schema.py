"""PCEC v0.1 Pydantic schemas for the agent pipeline.

Draft proposal — not a standard. Single operator (PawConscious) v0.1.
See docs/PCEC-v0.md for the full schema specification.
"""
from datetime import datetime
from enum import Enum
from typing import Optional, Any
from pydantic import BaseModel, Field


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
    grader_agent: str = "did:web:pawconscious.com:agents:evidence-grader"
    grader_run_id: Optional[str] = None


class VetRubricScore(BaseModel):
    claim: Claim
    score: int = Field(..., ge=1, le=5, description="5-vet rubric average")
    rationale: str
    escalate_to_human_vet: bool = False


class ComplianceMapping(BaseModel):
    claim: Claim
    ftc_section: Optional[str] = Field(None, description="e.g., '16 CFR §255.3'")
    aafco_definition: Optional[str] = None
    nasc_public_standard: Optional[str] = None
    violation_flag: bool = False
    rationale: str


class AuditVerdict(BaseModel):
    """Adversarial pass — citation existence + claim-direction match."""
    claim: Claim
    verdict: str = Field(..., description="PASS / FAIL / CONDITIONAL")
    challenges_run: list[str] = Field(default_factory=list)
    findings: list[str] = Field(default_factory=list)
    auditor_agent: str = "did:web:pawconscious.com:agents:auditor"


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
    issuer: str = "did:web:pawconscious.com"
    bundle_urn: Optional[str] = None
    signature: Optional[str] = None
