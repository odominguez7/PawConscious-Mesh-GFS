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

ENV PORT=8081
ENV PYTHONUNBUFFERED=1

EXPOSE 8081

CMD ["uvicorn", "services.shopper_agent.main:app", "--host", "0.0.0.0", "--port", "8081"]
