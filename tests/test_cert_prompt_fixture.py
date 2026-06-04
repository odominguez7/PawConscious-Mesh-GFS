"""Fast-path verification.

Renders the Agent 6 prompt against a JFFD-shaped fixture bundle and runs
a single Gemini 2.5 Pro call to verify the new prompt produces honest
cert HTML — without paying the 9-minute cost of a full mesh run.

Run on demand before deploy:
    cd PawConscious-GFS && source .venv/bin/activate
    python -m pytest tests/test_cert_prompt_fixture.py -v -s

Requires:
    GOOGLE_APPLICATION_CREDENTIALS or `gcloud auth application-default login`
    pawconscious-mesh-2026 project ADC

Output:
    1. Cert HTML pretty-printed to stdout for human review
    2. Honesty regex sweep — fails if any FORBIDDEN_PHRASES appear
    3. Semantic-diff contract — fails if required structure missing
"""
from __future__ import annotations

import asyncio
import json
import os
import re
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from tests.test_cert_honesty import _phrase_violations  # reuse the same matcher


FIXTURE_PATH = REPO_ROOT / "tests/fixtures/jffd_bundle.json"


@pytest.mark.fixture
def test_agent6_prompt_against_jffd_fixture() -> None:
    """Render the prompt + call Gemini + grep output. ~30s round trip.

    Gated behind env flag so default `pytest` runs DON'T fire this test
    on dev machines with ADC available. Opt in explicitly:
        AGENT6_FIXTURE_LIVE=1 python -m pytest tests/test_cert_prompt_fixture.py
    """
    # Explicit opt-in via env var; mark-only gating
    # doesn't actually prevent default-pytest execution.
    if not os.environ.get("AGENT6_FIXTURE_LIVE"):
        pytest.skip("AGENT6_FIXTURE_LIVE not set — fast-path Gemini call gated to opt-in")
    # Skip cleanly if no GCP credentials available
    if not (os.environ.get("GOOGLE_APPLICATION_CREDENTIALS") or
            Path.home().joinpath(".config/gcloud/application_default_credentials.json").exists()):
        pytest.skip("No ADC available — run `gcloud auth application-default login`")

    from agents.report_writer import compose_cert
    from shared.pcec_schema import (
        AuditVerdict, Claim, ClaimKind, ComplianceMapping,
        EndorsementClaimBundle, Evidence, EvidenceBundle, VetRubricScore,
    )

    data = json.loads(FIXTURE_PATH.read_text())
    # Rehydrate fixture into Pydantic models
    claims = [Claim(text=c["text"], kind=ClaimKind(c["kind"])) for c in data["claims"]]
    evidence = [
        EvidenceBundle(
            claim=claims[i],
            papers=[
                Evidence(pmid=p["pmid"], relevance_score=0.75, supports_claim_direction=True)
                for p in data["evidence"][i]["papers"]
            ],
        )
        for i in range(len(claims))
    ]
    vet_scores = [
        VetRubricScore(
            claim=claims[i],
            score=v["score"],
            rationale=v["rationale"],
            escalate_to_human_vet=v["escalate_to_human_vet"],
        )
        for i, v in enumerate(data["vet_scores"])
    ]
    compliance = [
        ComplianceMapping(
            claim=claims[i],
            ftc_section=c.get("ftc_section"),
            violation_flag=c["violation_flag"],
            rationale=c["rationale"],
        )
        for i, c in enumerate(data["compliance"])
    ]
    audit = [
        AuditVerdict(claim=claims[i], verdict=a["verdict"], findings=a.get("findings", []))
        for i, a in enumerate(data["audit"])
    ]
    bundle = EndorsementClaimBundle(
        sku=data["sku"],
        product_url=data["product_url"],
        bundle_urn=data["bundle_urn"],
        claims=claims,
        evidence=evidence,
        vet_scores=vet_scores,
        compliance=compliance,
        audit=audit,
    )

    cert_html = asyncio.run(compose_cert(
        bundle,
        bundle_hash="sha256:test-fixture-hash",
        chain_anchor="sha256:test-fixture-chain-anchor",
    ))

    print("\n" + "=" * 78)
    print("AGENT 6 OUTPUT (fixture run, ~" + str(len(cert_html)) + " bytes):")
    print("=" * 78)
    print(cert_html)
    print("=" * 78 + "\n")

    # 1. Honesty regex sweep
    violations = _phrase_violations(cert_html)
    assert not violations, (
        f"Agent 6 prompt produced overclaim language despite v0.10.1a fix:\n" +
        "\n".join(f"  · {p!r} at {i}: ...{s}..." for p, i, s in violations)
    )

    # 2. Semantic-diff contract — required structural elements
    # Gemini may add inline style/attrs to the wrapper div; check for the class
    # via regex rather than exact string match.
    required_regex = [
        (r"FAIL",                                 "overall verdict"),
        (r"<div[^>]*class=\"cert-composed\"",     "structural wrapper"),
        (r"vet[- ]rubric simulation",             "required phrasing dictionary"),
        (r"FTC\s*§255",                           "compliance reference"),
    ]
    missing = [label for regex, label in required_regex
               if not re.search(regex, cert_html, flags=re.IGNORECASE)]
    assert not missing, (
        f"Cert HTML missing required structural elements: {missing}.\n"
        f"Either the prompt over-corrected or Gemini drifted. Iterate."
    )

    # 3. Disclosure block must be present
    assert "Disclosure: AI-derived attestation" in cert_html, (
        "Inline disclosure block missing from cert footer. "
        "Check CERT_PROMPT substitution of {disclosure_inline}."
    )
    assert "Show full scope of attestation" in cert_html or "<details" in cert_html, (
        "Full <details> disclosure expander missing. "
        "Check CERT_PROMPT substitution of {disclosure_full_html}."
    )
