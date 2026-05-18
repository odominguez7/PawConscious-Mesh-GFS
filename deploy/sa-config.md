# Service Account Reference

## Runtime SA (for Cloud Run services)
**Email:** `acp-runtime@pawconscious-mesh-2026.iam.gserviceaccount.com`
**Roles bound:**
- roles/aiplatform.user (Gemini API access)
- roles/discoveryengine.user (Vertex AI Search)
- roles/bigquery.jobUser + roles/bigquery.user (BigQuery analytics)
- roles/storage.objectUser (Cloud Storage)
- roles/secretmanager.secretAccessor (Secret Manager)
- roles/datastore.user (Firestore for transparency log)
- roles/logging.logWriter (Cloud Logging)
- roles/monitoring.metricWriter (Cloud Monitoring)

## Deployer SA (for Cloud Build + Cloud Run deploy)
**Email:** `acp-deployer@pawconscious-mesh-2026.iam.gserviceaccount.com`
**Roles bound:**
- roles/run.admin (Cloud Run deploy)
- roles/iam.serviceAccountUser (act-as runtime SA)
- roles/artifactregistry.writer (push images)
- roles/cloudbuild.builds.builder (Cloud Build)
- roles/logging.logWriter

## Artifact Registry
**Repo:** `acp-images` (Docker, us-central1)
**Full path:** `us-central1-docker.pkg.dev/pawconscious-mesh-2026/acp-images`
