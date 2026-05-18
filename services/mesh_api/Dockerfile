# Dockerfile for PawConscious Mesh API (Cloud Run)
FROM python:3.13-slim

WORKDIR /app

# Install system deps for lxml + cryptography
RUN apt-get update && apt-get install -y --no-install-recommends \
    libxml2-dev libxslt1-dev gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy package metadata first for cache efficiency
COPY pyproject.toml ./

# Install Python deps
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
      google-adk \
      google-cloud-aiplatform \
      google-cloud-secret-manager \
      google-cloud-discoveryengine \
      google-cloud-firestore \
      httpx \
      beautifulsoup4 \
      lxml \
      fastapi \
      "uvicorn[standard]" \
      pydantic \
      cryptography \
      biomcp-python \
      mcp

# Copy application code
COPY shared/ ./shared/
COPY agents/ ./agents/
COPY services/mesh_api/ ./services/mesh_api/

ENV PORT=8080
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

EXPOSE 8080

CMD ["uvicorn", "services.mesh_api.main:app", "--host", "0.0.0.0", "--port", "8080"]
