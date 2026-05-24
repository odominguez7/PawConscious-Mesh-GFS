"""Agent 8 (NEW · 2026-05-24) — COA Ingester.

Multimodal evidence ingest. Takes a PDF (a brand's lab Certificate of Analysis,
or COA) and runs it through Google Cloud Document AI's OCR processor to extract
the ingredient table, lot/batch metadata, and any testing-method blocks. The
output attaches to the signed PCEC bundle under `attached_documents`, which is
the artifact the Vanta-for-claims narrative requires: real third-party
documents chained cryptographically to specific claims, not only LLM reasoning.

Why this exists:
- The previous 7-agent mesh signed LLM opinions over LLM-graded evidence.
- A plaintiff lawyer (or M&A diligence partner) reads that and pushes back:
  "you outsourced substantiation to an LLM."
- Document AI ingesting a real published COA puts a real third-party
  artifact in the bundle. The signature still proves "the mesh said this on
  date X," but now the bundle ALSO carries the source document a real
  accredited lab produced.

Processor:
- Type: OCR_PROCESSOR (Document OCR)
- Resource: projects/40952019806/locations/us/processors/41c510c3067b6d6d
- Created 2026-05-24 PM in pawconscious-mesh-2026 / us region.

Cost:
- Document OCR: $1.50 per 1000 pages (May 2024 pricing).
- An 8-page COA = $0.012 per call. Negligible for hackathon scope.

Honest scope of v1:
- Extracts free-text via OCR, then a Gemini 2.5 Flash pass identifies the
  ingredient table and pulls (name, amount, unit) tuples.
- Does NOT yet validate against AOAC method codes, ISO 17025 lab
  accreditation, or batch chain-of-custody. Those are roadmap items.
"""

from __future__ import annotations

import base64
import hashlib
import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional

from google.cloud import documentai_v1 as documentai
from google import genai
from google.genai import types as genai_types


# Locked at agent creation time. Set in code, not env, so the agent is
# self-contained and deployment-portable.
PROCESSOR_NAME = (
    "projects/40952019806/locations/us/processors/41c510c3067b6d6d"
)
PROCESSOR_REGION = "us"


@dataclass
class ExtractedFinding:
    """A single (ingredient, amount, unit) tuple parsed from the COA."""

    ingredient: str
    amount: str
    unit: str
    raw_context: str = ""  # surrounding line for traceability


@dataclass
class COAExtraction:
    """The full structured output of ingesting one COA PDF."""

    type: str = "coa"  # coa | lab_report | dvm_letter
    source_pdf_sha256: str = ""
    source_pdf_bytes: int = 0
    page_count: int = 0
    document_ai_processor: str = PROCESSOR_NAME
    raw_text: str = ""  # full OCR output (may be long)
    findings: list[ExtractedFinding] = field(default_factory=list)
    extracted_at: str = ""
    note: str = ""  # honest disclaimer string

    def to_bundle_dict(self) -> dict:
        """Shape ready to drop into PCECBundle.output.attached_documents[]."""
        return {
            "type": self.type,
            "source_pdf_sha256": self.source_pdf_sha256,
            "source_pdf_bytes": self.source_pdf_bytes,
            "page_count": self.page_count,
            "document_ai_processor": self.document_ai_processor,
            "findings": [asdict(f) for f in self.findings],
            "extracted_at": self.extracted_at,
            "note": self.note,
        }


def _docai_client() -> documentai.DocumentProcessorServiceClient:
    """Region-pinned client. The processor lives in `us`."""
    return documentai.DocumentProcessorServiceClient(
        client_options={
            "api_endpoint": f"{PROCESSOR_REGION}-documentai.googleapis.com"
        }
    )


def _run_ocr(pdf_bytes: bytes, *, max_pages: int = 15) -> tuple[str, int]:
    """Run Document AI OCR on the PDF bytes.

    Document AI Document OCR in image mode caps at 15 pages per request.
    COAs are typically structured with the ingredient findings table in the
    first few pages, so processing the first `max_pages` is sufficient.

    Returns (full_text, page_count). Raises on transport error; the caller
    decides whether to fail-closed or attach an UNAVAILABLE marker.
    """
    client = _docai_client()
    raw_document = documentai.RawDocument(
        content=pdf_bytes,
        mime_type="application/pdf",
    )
    request = documentai.ProcessRequest(
        name=PROCESSOR_NAME,
        raw_document=raw_document,
        process_options=documentai.ProcessOptions(
            from_start=max_pages,
        ),
    )
    response = client.process_document(request=request)
    document = response.document
    full_text = document.text or ""
    page_count = len(document.pages)
    return full_text, page_count


def _gemini_parse_findings(ocr_text: str) -> list[ExtractedFinding]:
    """Use Gemini 2.5 Flash to identify (ingredient, amount, unit) tuples
    from the OCR output. Honest about why we use an LLM here: the COA layout
    varies wildly across labs and we are not yet building a per-lab
    structured parser. v0.2 will use a Document AI Custom Extractor trained
    on labeled COAs.
    """
    if not ocr_text.strip():
        return []

    client = genai.Client(vertexai=True, project="pawconscious-mesh-2026", location="us-central1")
    prompt = (
        "You are extracting ingredient findings from an accredited lab's "
        "Certificate of Analysis (COA) for a pet supplement. Find every "
        "ingredient with a measured amount and unit. Skip the testing methods, "
        "the lab address, and the lot/batch metadata. Output a JSON array "
        "where each item is {\"ingredient\": str, \"amount\": str, "
        "\"unit\": str, \"raw_context\": str}. Output ONLY the JSON array, "
        "no prose, no markdown fence. If you cannot find any ingredients, "
        "return [].\n\n"
        f"COA text:\n{ocr_text[:18000]}"
    )

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=genai_types.GenerateContentConfig(
            temperature=0.0,
            response_mime_type="application/json",
        ),
    )

    try:
        payload = json.loads(response.text or "[]")
    except json.JSONDecodeError:
        return []

    findings: list[ExtractedFinding] = []
    for item in payload if isinstance(payload, list) else []:
        if not isinstance(item, dict):
            continue
        findings.append(
            ExtractedFinding(
                ingredient=str(item.get("ingredient", "")).strip(),
                amount=str(item.get("amount", "")).strip(),
                unit=str(item.get("unit", "")).strip(),
                raw_context=str(item.get("raw_context", "")).strip(),
            )
        )
    return findings


def ingest_coa(
    pdf_bytes: bytes,
    *,
    label: Optional[str] = None,
) -> COAExtraction:
    """End-to-end ingest of a COA PDF.

    Args:
        pdf_bytes: the raw PDF content.
        label: optional friendly label for the source (e.g. brand + product).
            Stored in the `note` field for traceability.

    Returns:
        A COAExtraction ready to attach to a PCECBundle.
    """
    from datetime import datetime, timezone

    sha = hashlib.sha256(pdf_bytes).hexdigest()
    note_parts = ["Document AI OCR + Gemini 2.5 Flash field parsing"]
    if label:
        note_parts.append(label)

    try:
        raw_text, page_count = _run_ocr(pdf_bytes)
    except Exception as exc:  # pragma: no cover - transport failure
        return COAExtraction(
            source_pdf_sha256=sha,
            source_pdf_bytes=len(pdf_bytes),
            extracted_at=datetime.now(timezone.utc).isoformat(),
            note=" · ".join(note_parts + [f"OCR_UNAVAILABLE: {exc!s}"]),
        )

    findings = _gemini_parse_findings(raw_text)

    return COAExtraction(
        source_pdf_sha256=sha,
        source_pdf_bytes=len(pdf_bytes),
        page_count=page_count,
        raw_text=raw_text,
        findings=findings,
        extracted_at=datetime.now(timezone.utc).isoformat(),
        note=" · ".join(note_parts),
    )


def main() -> None:
    """CLI smoke test: python agents/coa_ingester.py corpus/coa/green-gruff-ease-joint-hip.pdf"""
    import sys

    if len(sys.argv) < 2:
        print(
            "Usage: python agents/coa_ingester.py <pdf_path>",
            file=sys.stderr,
        )
        sys.exit(1)

    path = Path(sys.argv[1])
    if not path.exists():
        print(f"File not found: {path}", file=sys.stderr)
        sys.exit(1)

    print(f"Ingesting: {path}")
    pdf = path.read_bytes()
    result = ingest_coa(pdf, label=path.stem)

    print(f"\nSHA256: {result.source_pdf_sha256[:16]}…")
    print(f"Pages: {result.page_count}")
    print(f"Note: {result.note}")
    print(f"OCR text length: {len(result.raw_text)} chars")
    print(f"\nExtracted findings ({len(result.findings)}):")
    for i, f in enumerate(result.findings, 1):
        print(f"  {i}. {f.ingredient}: {f.amount} {f.unit}")

    bundle_payload = result.to_bundle_dict()
    bundle_payload["raw_text_preview"] = (result.raw_text[:400] + "…") if result.raw_text else ""
    print("\nBundle payload preview (raw_text truncated):")
    bundle_payload_no_text = {k: v for k, v in bundle_payload.items()}
    print(json.dumps(bundle_payload_no_text, indent=2, default=str)[:1500])


if __name__ == "__main__":
    main()
