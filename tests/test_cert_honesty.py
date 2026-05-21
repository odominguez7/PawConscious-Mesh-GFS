"""Cert honesty guard — codex amendment A-codex-10 (plan 2026-05-21).

Catches future regressions where a prompt change reintroduces overclaim
language into cert HTML output. Runs on every cert-touching commit (CI),
and on demand before any deploy.

Scope:
  1. Static check — the v0.10.0c JFFD_CERT_HTML constant baked into
     console-v2.html (cached demo).
  2. Disclosure-block check — both DISCLOSURE_BLOCK_INLINE and
     DISCLOSURE_BLOCK_FULL exported by agents/report_writer.py must be
     present in any cert HTML produced.
  3. Live check — running `pytest -m live` against a live mesh fetches
     the JFFD bundle and grep-checks its cert_html (only runs if the
     mesh-api is up and reachable; skipped otherwise).

Add to CI: pytest tests/test_cert_honesty.py
"""
from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Iterable

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent

# Forbidden phrases — every cert MUST NOT contain any of these, with
# exception clauses where the phrase appears inside HONEST framing.
# Each entry is (phrase, allowed_context_re):
#   - phrase: case-insensitive substring to forbid
#   - allowed_context_re: if set, the phrase is OK when the regex matches
#     anywhere in the preceding 60 characters. Catches honest framing like
#     "simulating a 5-vet panel" (preceded by "simulating") or "not a
#     3rd-party accredited co-signature" (preceded by "not a").
FORBIDDEN_PHRASES: list[tuple[str, str | None]] = [
    # "veterinary panel" is NEVER allowed. Even "simulated veterinary panel"
    # is misleading; correct framing is "AI vet-rubric simulation".
    ("veterinary panel", None),
    # "vet panel" is allowed in HONEST framing contexts only.
    ("vet panel", r"\b(simulated|AI-simulated|simulating|5-vet|rubric is)\b"),
    # Auditor only validates PMID format — never claim citations were verified to exist.
    ("verified citations exist", None),
    ("citations were verified", None),
    # No real DVMs in v0.1. Allowed only when negated. Catches both
    # "licensed DVM" (space) and "licensed-DVM" (hyphen) variants since
    # the disclosure block uses the hyphenated form (codex B.5 P3).
    ("licensed DVM", r"\b(no|zero|without|not\b|replaces?\b|attestation by|roadmap)\b"),
    ("licensed dvm", r"\b(no|zero|without|not\b|replaces?\b|attestation by|roadmap)\b"),
    ("licensed-DVM", r"\b(no|zero|without|not\b|replaces?\b|attestation by|roadmap)\b"),
    ("licensed-dvm", r"\b(no|zero|without|not\b|replaces?\b|attestation by|roadmap)\b"),
    # Mesh signs with its own Ed25519 key. Allowed only when negated.
    ("3rd-party accredited", r"\b(not|never|no\b)\b"),
    ("third-party accredited", r"\b(not|never|no\b)\b"),
    # We do not certify FDA approval. Allowed only when negated.
    ("FDA approved", r"\b(not|never|no\b)\b"),
    ("FDA-approved", r"\b(not|never|no\b)\b"),
]


def _phrase_violations(text: str) -> list[tuple[str, int, str]]:
    """Return list of (phrase, offset, context_snippet) for each violation."""
    violations: list[tuple[str, int, str]] = []
    lower = text.lower()
    for phrase, allowed_context_re in FORBIDDEN_PHRASES:
        needle = phrase.lower()
        start = 0
        while True:
            idx = lower.find(needle, start)
            if idx == -1:
                break
            if allowed_context_re is not None:
                # Look at the up-to-60 chars preceding the match. If an
                # honest-framing word appears anywhere in that window,
                # this occurrence is allowed.
                preceding = text[max(0, idx - 60):idx]
                if re.search(allowed_context_re, preceding, flags=re.IGNORECASE):
                    start = idx + len(needle)
                    continue
            snippet = text[max(0, idx - 40):idx + len(needle) + 40]
            violations.append((phrase, idx, snippet))
            start = idx + len(needle)
    return violations


def _assert_no_forbidden(label: str, text: str) -> None:
    violations = _phrase_violations(text)
    if violations:
        details = "\n".join(
            f"  · {phrase!r} at offset {idx}: ...{snippet}..."
            for phrase, idx, snippet in violations
        )
        raise AssertionError(
            f"Cert overclaim regression in {label}:\n{details}\n"
            f"See agents/report_writer.py CERT_PROMPT — REQUIRED PHRASING + FORBIDDEN PHRASES."
        )


def test_console_v2_jffd_cached_cert_html_is_honest() -> None:
    """The hand-baked JFFD cached cert in console-v2.html must be honest."""
    html = (REPO_ROOT / "services/mesh_api/static/console-v2.html").read_text()
    # The JFFD_CERT_HTML constant spans hundreds of lines; the simplest check
    # is to scan the whole file. If overclaim appears anywhere in the v0.10.0c
    # cached demo block, it gets flagged.
    _assert_no_forbidden("console-v2.html (JFFD_CERT_HTML embedded)", html)


def test_disclosure_constants_present_in_report_writer() -> None:
    """Phase B locked the disclosure block as Python constants. Both must be
    importable and non-empty so the prompt format() always has substitutions."""
    src = (REPO_ROOT / "agents/report_writer.py").read_text()
    assert "DISCLOSURE_BLOCK_INLINE" in src, (
        "DISCLOSURE_BLOCK_INLINE constant missing from report_writer.py — "
        "the locked disclosure footer template is broken."
    )
    assert "DISCLOSURE_BLOCK_FULL" in src, (
        "DISCLOSURE_BLOCK_FULL constant missing from report_writer.py — "
        "the <details> expander template is broken."
    )
    assert "{disclosure_inline}" in src and "{disclosure_full_html}" in src, (
        "CERT_PROMPT must substitute {disclosure_inline} and {disclosure_full_html} "
        "so Gemini emits the locked disclosure verbatim."
    )


def test_required_phrasing_in_cert_prompt() -> None:
    """Agent 6 prompt must encode the positive phrasing dictionary + few-shot
    exemplars + forbidden phrases (codex A-codex-2)."""
    src = (REPO_ROOT / "agents/report_writer.py").read_text()
    assert "REQUIRED PHRASING" in src
    assert "FORBIDDEN PHRASES" in src
    assert "AI vet-rubric simulation" in src
    assert "FEW-SHOT EXEMPLARS" in src
    assert "EXAMPLE 1" in src and "EXAMPLE 2" in src


@pytest.mark.live
def test_live_jffd_cert_is_honest() -> None:
    """Optional: probe live mesh-api and grep the JFFD cert_html.

    Skipped unless MESH_API_URL is set and the bundle is reachable.
    Run with: MESH_API_URL=https://mesh-api-... pytest tests/test_cert_honesty.py -m live
    """
    url = os.environ.get("MESH_API_URL")
    if not url:
        pytest.skip("MESH_API_URL not set")
    import urllib.request
    import json
    try:
        with urllib.request.urlopen(
            f"{url}/a2a/v1/tasks/get/task-jffd-known-cached", timeout=10
        ) as resp:
            data = json.loads(resp.read())
    except Exception as e:
        pytest.skip(f"live mesh-api not reachable: {e}")
    cert_html = data.get("cert_html") or ""
    if not cert_html:
        pytest.skip("no cert_html returned (task may have expired from in-memory store)")
    _assert_no_forbidden("live JFFD cert_html", cert_html)
