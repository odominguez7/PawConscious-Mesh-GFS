"""Provision Vertex AI Search data store + ingest regulator corpus from GCS.

Per codex G13 Phase 8: "smallest credible corpus = FTC §255 text + 3-5 AAFCO public docs"
We ingest 7 docs (5 FTC §255 sections + AAFCO PF7 + NASC public).

After this script runs, the compliance agent can use Vertex AI Search as a
Gemini grounding source for regulator-text retrieval.
"""
from __future__ import annotations

import sys
import time
from typing import Optional

from google.api_core.client_options import ClientOptions
from google.cloud import discoveryengine
from google.cloud.discoveryengine_v1 import (
    DataStoreServiceClient, DocumentServiceClient,
    CreateDataStoreRequest, DataStore, ImportDocumentsRequest, GcsSource,
)


PROJECT = "pawconscious-mesh-2026"
LOCATION = "global"  # Discovery Engine data stores in 'global' region
DATA_STORE_ID = "acp-regulator-corpus"
BUCKET = "gs://pawconscious-mesh-2026-corpus/*.txt"


def get_client_options() -> ClientOptions:
    if LOCATION == "global":
        return ClientOptions(api_endpoint="discoveryengine.googleapis.com")
    return ClientOptions(api_endpoint=f"{LOCATION}-discoveryengine.googleapis.com")


def create_data_store() -> str:
    client = DataStoreServiceClient(client_options=get_client_options())
    collection = client.collection_path(PROJECT, LOCATION, "default_collection")

    request = CreateDataStoreRequest(
        parent=collection,
        data_store_id=DATA_STORE_ID,
        data_store=DataStore(
            display_name="ACP Regulator Corpus (FTC §255 + AAFCO + NASC public)",
            industry_vertical=discoveryengine.IndustryVertical.GENERIC,
            solution_types=[discoveryengine.SolutionType.SOLUTION_TYPE_SEARCH],
            content_config=DataStore.ContentConfig.CONTENT_REQUIRED,
        ),
    )
    operation = client.create_data_store(request=request)
    print(f"Creating data store: {operation.operation.name}")
    response = operation.result(timeout=300)
    print(f"Created: {response.name}")
    return response.name


def import_documents(data_store_name: str) -> None:
    client = DocumentServiceClient(client_options=get_client_options())
    parent = (
        f"projects/{PROJECT}/locations/{LOCATION}/collections/default_collection/"
        f"dataStores/{DATA_STORE_ID}/branches/0"
    )
    request = ImportDocumentsRequest(
        parent=parent,
        gcs_source=GcsSource(input_uris=[BUCKET], data_schema="content"),
        reconciliation_mode=ImportDocumentsRequest.ReconciliationMode.INCREMENTAL,
    )
    operation = client.import_documents(request=request)
    print(f"Importing documents: {operation.operation.name}")
    print("Polling for completion (may take 2-5 min)...")
    for i in range(60):  # 5-min max poll
        time.sleep(5)
        op = client.transport.operations_client.get_operation(operation.operation.name)
        if op.done:
            print(f"Import done: {op.response or op.error}")
            return
        if i % 4 == 0:
            print(f"  still importing... ({(i+1)*5}s)")
    print("Import did not complete in 5 min — check console for status")


def main() -> None:
    if "--skip-create" not in sys.argv:
        try:
            data_store_name = create_data_store()
        except Exception as e:
            if "already exists" in str(e).lower():
                data_store_name = (
                    f"projects/{PROJECT}/locations/{LOCATION}/collections/default_collection/"
                    f"dataStores/{DATA_STORE_ID}"
                )
                print(f"Data store already exists: {data_store_name}")
            else:
                raise
    else:
        data_store_name = (
            f"projects/{PROJECT}/locations/{LOCATION}/collections/default_collection/"
            f"dataStores/{DATA_STORE_ID}"
        )

    import_documents(data_store_name)
    print()
    print(f"✅ Data store ready: {data_store_name}")
    print(f"   Use this resource path in Gemini grounding config.")


if __name__ == "__main__":
    main()
