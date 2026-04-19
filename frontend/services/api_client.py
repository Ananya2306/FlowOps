"""
api_client.py
Thin wrapper around the FlowOps FastAPI backend.
Centralizes all HTTP calls so the UI layer stays clean.
"""

import requests
from typing import Optional

BASE_URL = "https://flowops-b2gv.onrender.com"
TIMEOUT  = 5  # seconds


def _get(path: str) -> dict:
    r = requests.get(f"{BASE_URL}{path}", timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()


def _post(path: str, body: dict | None = None) -> dict:
    r = requests.post(f"{BASE_URL}{path}", json=body or {}, timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()


# ── Public helpers ────────────────────────────────────────────────────────────

def fetch_zones() -> dict:
    """GET /zones — returns full VenueState."""
    return _get("/zones/")


def fetch_recommendation() -> dict:
    """GET /recommendation — returns best exit + alternative."""
    return _get("/recommendation")


def post_simulate(surge_zone: Optional[str] = None,
                  surge_magnitude: float = 0.2,
                  tick_count: int = 1) -> dict:
    """POST /simulate — advance simulation, optionally with a surge."""
    return _post("/simulate", {
        "surge_zone": surge_zone,
        "surge_magnitude": surge_magnitude,
        "tick_count": tick_count,
    })


def post_reset() -> dict:
    """POST /reset — restore default crowd state."""
    return _post("/reset")


def check_health() -> bool:
    try:
        data = _get("/health")
        return data.get("status") == "ok"
    except Exception:
        return False
