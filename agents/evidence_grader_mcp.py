"""Evidence Grader via MCP Protocol (Phase 3.5 — codex G9 + G10 requirement).

Replaces the direct biomcp Python lib import with proper MCP protocol usage:
- Spawn `biomcp run --mode stdio` as a subprocess
- Connect via mcp.client.stdio.stdio_client
- Call tools via ClientSession protocol

Per codex G10 #3: A2A public-facing endpoint promises MCP compliance, so this
wrap MUST land before Phase 4 ships.

The original direct-lib evidence_grader.py is preserved as a reference and a
fallback if the MCP subprocess fails during the demo.
"""
from __future__ import annotations

import asyncio
import json
import re
import sys
from contextlib import asynccontextmanager
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from shared.pcec_schema import Claim, ClaimKind, Evidence, EvidenceBundle  # noqa: E402
from agents.evidence_grader import (  # noqa: E402
    GRADING_PROMPT, KEYWORD_EXTRACTION_PROMPT, PMID_REGEX,
    extract_search_terms, grade_evidence,
)

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


BIOMCP_SERVER_PARAMS = StdioServerParameters(
    command="biomcp",
    args=["run", "--mode", "stdio"],
)


@asynccontextmanager
async def biomcp_session():
    """Spawn biomcp as a subprocess + open an MCP ClientSession."""
    async with stdio_client(BIOMCP_SERVER_PARAMS) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            yield session


async def search_pubmed_via_mcp(claim: Claim, limit: int = 10, debug: bool = False) -> str:
    """Query PubMed via the BioMCP MCP server (protocol-compliant)."""
    terms = await extract_search_terms(claim)
    capped = {
        "keywords": terms["keywords"][:2],
        "chemicals": terms["chemicals"][:2],
        "diseases": terms["diseases"][:2],
    }
    if debug:
        print(f"[mcp] capped terms: {capped}")

    async with biomcp_session() as session:
        # Discover available tools (per MCP spec)
        tools_resp = await session.list_tools()
        tool_names = [t.name for t in tools_resp.tools]
        if debug:
            print(f"[mcp] available tools: {tool_names[:10]}")

        # The BioMCP article search tool is named 'article_searcher' or similar
        # Pick the right one dynamically
        search_tool = None
        for candidate in ("article_searcher", "search_articles", "article_search"):
            if candidate in tool_names:
                search_tool = candidate
                break
        if search_tool is None:
            # Try a partial match
            for name in tool_names:
                if "article" in name.lower() and "search" in name.lower():
                    search_tool = name
                    break
        if search_tool is None:
            raise RuntimeError(f"No article search tool found in BioMCP. Available: {tool_names}")

        if debug:
            print(f"[mcp] using tool: {search_tool}")

        # Call the tool via MCP protocol
        result = await session.call_tool(
            search_tool,
            arguments={
                "keywords": capped["keywords"],
                "chemicals": capped["chemicals"],
                "diseases": capped["diseases"],
                "limit": limit,
            },
        )

        # MCP returns a list of content items; concatenate text content
        texts: list[str] = []
        for item in result.content:
            if hasattr(item, "text"):
                texts.append(item.text)
        return "\n".join(texts)


async def grade_claim_via_mcp(claim: Claim, debug: bool = False) -> EvidenceBundle:
    """End-to-end via MCP protocol: claim in, EvidenceBundle out with real PMIDs."""
    search_results = await search_pubmed_via_mcp(claim, debug=debug)
    if debug:
        print(f"[mcp] search_results length: {len(search_results)}")
    papers = await grade_evidence(claim, search_results, debug=debug)
    return EvidenceBundle(
        claim=claim,
        papers=papers,
        grader_agent="did:web:pawconscious.com:agents:evidence-grader-mcp",
        grader_run_id=None,
    )


async def main() -> None:
    """Phase 3.5 verification: BioMCP via MCP protocol returns real PMIDs."""
    test_claim = Claim(
        text="Supports joint health and mobility",
        kind=ClaimKind.EFFICACY,
        position_on_page="description",
        raw_context="chondroitin and turmeric for joint health",
    )

    print(f"Grading via MCP protocol: {test_claim.text!r}\n")
    bundle = await grade_claim_via_mcp(test_claim, debug=True)
    print(f"\nReturned {len(bundle.papers)} graded papers (via MCP):")
    for i, e in enumerate(bundle.papers, 1):
        direction = "supports" if e.supports_claim_direction else "contradicts/neutral"
        print(f"{i}. PMID {e.pmid} | relevance {e.relevance_score:.2f} | {direction}")


if __name__ == "__main__":
    asyncio.run(main())
