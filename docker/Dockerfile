# ── Stage 1: build deps ───────────────────────────────────────────────────────
FROM python:3.11-slim AS base

WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Stage 2: app 
FROM base AS app

WORKDIR /app
COPY . .

# Expose both ports
EXPOSE 8000 8501

# Default: start FastAPI backend
CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8000"]
