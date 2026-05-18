# Dockerfile for ShopperAgent (Cloud Run)
FROM python:3.13-slim

WORKDIR /app

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
      httpx \
      fastapi \
      "uvicorn[standard]" \
      pydantic

COPY services/shopper_agent/ ./services/shopper_agent/

ENV PYTHONUNBUFFERED=1

EXPOSE 8080

# Cloud Run injects PORT env var; sh -c expands it
CMD exec uvicorn services.shopper_agent.main:app --host 0.0.0.0 --port ${PORT:-8080}
