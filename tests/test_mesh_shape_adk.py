"""R3 Day 20 — ADK topology shape tests.

Verifies the SequentialAgent + ParallelAgent declarations are well-formed and
introspectable. No live LLM calls; runtime continues on asyncio.gather. These
tests pin the structural claim 'X agents on ADK' so a refactor that loses an
agent breaks the build.
"""
from __future__ import annotations

import pytest


def test_topology_is_built_and_cached():
    from agents.orchestrator import build_orchestrator_adk_topology
    t1 = build_orchestrator_adk_topology()
    t2 = build_orchestrator_adk_topology()
    assert t1 is t2, "topology must be cached — ADK enforces single-parent on agents"


def test_topology_root_is_sequential_agent():
    from google.adk.agents import SequentialAgent
    from agents.orchestrator import build_orchestrator_adk_topology
    root = build_orchestrator_adk_topology()
    assert isinstance(root, SequentialAgent)
    assert root.name == "acp_orchestrator"


def test_topology_second_child_is_parallel_fan_out():
    """Day 21: topology is [claim_extractor, fan_out, auditor] — fan_out is at index 1."""
    from google.adk.agents import ParallelAgent
    from agents.orchestrator import build_orchestrator_adk_topology
    root = build_orchestrator_adk_topology()
    fan_out = root.sub_agents[1]
    assert isinstance(fan_out, ParallelAgent)
    assert fan_out.name == "acp_claim_fan_out"


def test_topology_third_child_is_auditor_llm_agent():
    from google.adk.agents import LlmAgent
    from agents.orchestrator import build_orchestrator_adk_topology
    root = build_orchestrator_adk_topology()
    auditor = root.sub_agents[2]
    assert isinstance(auditor, LlmAgent)
    assert auditor.name == "acp_auditor"
    assert auditor.model == "gemini-2.5-flash"
    assert auditor.output_key == "audit_verdict"


def test_topology_includes_claim_extractor_first():
    """Day 21: claim_extractor is the first child of the SequentialAgent —
    runs once per URL before per-claim fan-out."""
    from google.adk.agents import LlmAgent
    from agents.orchestrator import build_orchestrator_adk_topology
    root = build_orchestrator_adk_topology()
    first = root.sub_agents[0]
    assert isinstance(first, LlmAgent)
    assert first.name == "claim_extractor"


def test_evidence_grader_is_llm_agent_with_search_tool():
    from google.adk.agents import LlmAgent
    from agents.orchestrator import build_orchestrator_adk_topology
    root = build_orchestrator_adk_topology()
    # After Day 21 the topology is: [claim_extractor, fan_out, auditor].
    # fan_out is at index 1; its children are evidence_grader + compliance.
    fan_out = root.sub_agents[1]
    grader = next(a for a in fan_out.sub_agents if a.name == "acp_evidence_grader")
    assert isinstance(grader, LlmAgent)
    assert grader.model == "gemini-2.5-pro"
    assert grader.output_key == "evidence_bundle"
    tool_names = [getattr(t, "name", getattr(t.func, "__name__", "")) for t in grader.tools]
    assert "search_pubmed_for_adk" in tool_names


def test_compliance_is_llm_agent_with_vertex_search_tool():
    """Day 21: compliance is in the per-claim fan-out alongside evidence_grader."""
    from google.adk.agents import LlmAgent
    from agents.orchestrator import build_orchestrator_adk_topology
    root = build_orchestrator_adk_topology()
    fan_out = root.sub_agents[1]
    compliance = next(a for a in fan_out.sub_agents if a.name == "acp_compliance")
    assert isinstance(compliance, LlmAgent)
    assert compliance.model == "gemini-2.5-pro"
    assert compliance.output_key == "compliance_mapping"
    tool_names = [getattr(t, "name", getattr(t.func, "__name__", "")) for t in compliance.tools]
    assert "retrieve_grounding_sources_for_adk" in tool_names


def test_describe_mesh_shape_returns_judge_safe_json():
    """The /health/mesh-shape JSON must contain enough for a Track 3 evaluator
    to verify the multi-agent claim without invoking an LLM."""
    import json
    from agents.orchestrator import describe_mesh_shape
    shape = describe_mesh_shape()
    # Round-trip through json — no non-serializable values allowed.
    json.dumps(shape)
    assert shape["adk_version"] != "unknown"
    assert "acp_evidence_grader" in shape["agents_on_adk"]
    assert "acp_auditor" in shape["agents_on_adk"]
    assert "acp_compliance" in shape["agents_on_adk"]
    assert "acp_claim_extractor" in shape["agents_on_adk"]
    assert shape["ratio_on_adk"] == "4/7"
    assert "vet_rubric" in shape["agents_off_adk_by_design"]
    # Root + deep introspection: Day 21 = [claim_extractor, fan_out, auditor]
    root = shape["root"]
    assert root["name"] == "acp_orchestrator"
    assert root["type"] == "SequentialAgent"
    assert len(root["sub_agents"]) == 3


def test_runtime_path_disclosed_honestly():
    """Track 3 evaluator must be able to read the runtime/shape boundary
    without crawling code. The note must surface the asyncio runtime path."""
    from agents.orchestrator import describe_mesh_shape
    shape = describe_mesh_shape()
    assert "asyncio" in shape["runtime_path"]
    assert "shape" in shape["runtime_path"].lower()


def test_adk_eval_cases_have_synthetic_track():
    """R4: synthetic-fixture eval track exists as a separate scoreboard. Never
    merged with the live-URL track. 5 fixture cases covering canonical
    efficacy / clinical-disease language / puffery / specific-percentage /
    bare endorsement claim kinds."""
    import json
    from pathlib import Path
    cases_path = Path(__file__).parent / "adk_eval" / "cases.json"
    data = json.loads(cases_path.read_text())
    assert "_synthetic_cases" in data
    syn = data["_synthetic_cases"]
    assert len(syn) >= 5
    # Each synthetic case must have claim text and expected outcomes
    for c in syn:
        assert c.get("claim_text"), f"synthetic case {c.get('id')} missing claim_text"
        assert "expected_compliance_violation" in c, f"{c.get('id')} missing compliance expectation"
    # Live-URL track must remain populated post-refresh
    assert len(data["cases"]) >= 15, "main eval should have 15+ live URLs post-R4"
    assert data["_meta"]["spec_version"] == "0.2"


def test_search_pubmed_for_adk_returns_string():
    """Codex Day-20 P2: BioMCP's search_articles returns markdown text, not JSON.
    The FunctionTool wrapper must return a string so a downstream LlmAgent's
    tool-output contract is text the model can read; calling json.loads on it
    would have raised JSONDecodeError on the first ADK invocation."""
    from typing import get_type_hints
    from agents.evidence_grader import search_pubmed_for_adk
    hints = get_type_hints(search_pubmed_for_adk)
    assert hints.get("return") is str, (
        f"search_pubmed_for_adk must return str (markdown), got "
        f"{hints.get('return')!r}"
    )
