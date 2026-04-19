"""
app.py  —  FlowOps Backend
Real-time crowd flow optimization API for large-venue exit management.

Run locally:
    uvicorn backend.app:app --reload --port 8000

Docs at: http://localhost:8000/docs
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timezone

from backend.routes.zones import router as zones_router
from backend.routes.recommendation import router as rec_router
from backend.models.schema import HealthResponse

# ── App init ──────────────────────────────────────────────────────────────────
app = FastAPI(
    title="FlowOps API",
    description=(
        "Real-time crowd flow optimization for large venues. "
        "Provides live exit zone status, AI-driven routing recommendations, "
        "and a configurable simulation engine."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(zones_router)
app.include_router(rec_router)


# ── Health check ──────────────────────────────────────────────────────────────
@app.get("/health", response_model=HealthResponse, tags=["meta"])
async def health():
    return HealthResponse(
        status="ok",
        version="1.0.0",
        timestamp=datetime.now(timezone.utc),
    )


@app.get("/", tags=["meta"])
async def root():
    return {
        "project": "FlowOps",
        "tagline": "Real-time crowd flow optimization for large venues",
        "docs": "/docs",
        "health": "/health",
    }
