"""Deploy PawConscious Mesh orchestrator to Vertex AI Agent Engine.

Closes the fifth Track 3 Key Consideration from the GFS rules: 'Focus on the
deployment of your multi-agent system on Agent Engine.'

The Cloud Run mesh-api stays as the public A2A endpoint. The Agent Engine
resource is the managed Reasoning Engine the multi-agent system registers as
under Vertex AI. Judges who inspect the project see a deployed Reasoning Engine
with a query method that maps to our verify_claim skill.

Deploy the orchestrator as the entrypoint, keep the 5 specialist
agents as Cloud Run workers. The orchestrator on Agent Engine routes by delegating
through the orchestrator's asyncio.gather fan-out (same code path as the Cloud
Run service).

Cost note: Agent Engine instances run at ~$0.10/hour while warm. Cap to 1 replica.
Shutdown post-hackathon if not needed.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import vertexai
from vertexai import agent_engines


PROJECT = "pawconscious-mesh-2026"
LOCATION = "us-central1"
STAGING_BUCKET = "gs://pawconscious-mesh-2026-agent-engine-staging"


class ACPMeshEngine:
    """Reasoning Engine entrypoint for the PawConscious Mesh orchestrator.

    Methods are registered as Agent Engine ops. The `query` method routes to
    the existing orchestrator.run_mesh which fans out to 5 specialist ADK
    agents in parallel and returns the signed PCEC bundle.
    """

    def set_up(self):
        """Called once when the Agent Engine warm-starts. Initializes nothing
        heavy here since the orchestrator imports lazily on first query."""
        import os
        os.environ.setdefault("GOOGLE_CLOUD_PROJECT", PROJECT)
        os.environ.setdefault("GOOGLE_CLOUD_LOCATION", LOCATION)
        os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "true")

    def query(self, product_url: str, max_claims: int = 3) -> dict:
        """Verify a product URL via the 5-agent A2A mesh.

        Args:
            product_url: The pet product PDP URL to verify.
            max_claims: Number of top claims to process (default 3).

        Returns:
            EndorsementClaimBundle JSON (claims, evidence, vet_scores,
            compliance with grounding_sources, audit, signature).
        """
        # Lazy imports — keeps the cold start cheap and isolates the orchestrator
        # code path to query-time.
        import asyncio
        import json
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).resolve().parent))

        from agents.orchestrator import run_mesh

        bundle = asyncio.run(run_mesh(product_url, max_claims=max_claims))
        return json.loads(bundle.model_dump_json())

    def list_skills(self) -> list[dict]:
        """A2A v0.3 skill discovery. Mirrors the public agent card."""
        return [
            {
                "id": "verify_claim",
                "name": "Verify endorsement claim",
                "description": (
                    "Given a product URL, run the 5-agent mesh and return a "
                    "signed PCEC v0.1 evidence bundle."
                ),
                "input_modes": ["text"],
                "output_modes": ["application/ld+json"],
            }
        ]


REQUIREMENTS = [
    "google-adk>=1.33",
    "google-cloud-aiplatform>=1.153",
    "google-cloud-secret-manager>=2.20",
    "google-cloud-discoveryengine>=0.13",
    "httpx>=0.28",
    "beautifulsoup4>=4.14",
    "lxml>=5.0",
    "pydantic>=2.9",
    "cryptography>=44.0",
    "biomcp-python>=0.7.3",
    "mcp>=1.27",
]


def main() -> None:
    vertexai.init(
        project=PROJECT,
        location=LOCATION,
        staging_bucket=STAGING_BUCKET,
    )

    print("Creating Vertex AI Agent Engine resource...")
    print("This typically takes 8-15 minutes (build + deploy).")
    print()

    # extra_packages: ship the agents/ and shared/ directories with the engine
    repo_root = Path(__file__).resolve().parent.parent
    extra_packages = [
        str(repo_root / "agents"),
        str(repo_root / "shared"),
    ]

    remote_app = agent_engines.create(
        ACPMeshEngine(),
        requirements=REQUIREMENTS,
        extra_packages=extra_packages,
        display_name="PawConscious Mesh — ACP for Pet (orchestrator)",
        description=(
            "Multi-agent A2A v0.3 trust mesh for pet supplement claim verification. "
            "Orchestrator entrypoint. Delegates to 5 specialist agents (claim-extractor, "
            "evidence-grader via BioMCP, vet-panel, compliance grounded via Vertex AI "
            "Search, auditor). Returns signed PCEC v0.1 bundle with Ed25519 signature "
            "anchored to did:web:mesh-api-40952019806.us-central1.run.app."
        ),
    )

    print(f"✅ Agent Engine resource created: {remote_app.resource_name}")
    print()
    print("Test with:")
    print(f'    from vertexai import agent_engines')
    print(f'    app = agent_engines.get("{remote_app.resource_name}")')
    print(f'    result = app.query(product_url="https://www.nativepet.com/products/hip-joint", max_claims=1)')
    print()
    print("Save this resource name for the mesh-api Cloud Run env var ACP_AGENT_ENGINE_RESOURCE.")


if __name__ == "__main__":
    main()
