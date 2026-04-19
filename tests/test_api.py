"""
test_api.py
Integration tests for FlowOps FastAPI backend.

Run:
    pytest tests/test_api.py -v
"""

import pytest
from fastapi.testclient import TestClient
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from backend.app import app

client = TestClient(app)


# ── Health & root ─────────────────────────────────────────────────────────────

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert "version" in data
    assert "timestamp" in data


def test_root():
    r = client.get("/")
    assert r.status_code == 200
    assert r.json()["project"] == "FlowOps"


# ── Zones ─────────────────────────────────────────────────────────────────────

def test_get_zones():
    r = client.get("/zones/")
    assert r.status_code == 200
    data = r.json()

    assert "zones" in data
    assert "total_crowd" in data
    assert len(data["zones"]) > 0

    for zone in data["zones"]:
        assert "id" in zone
        assert "density" in zone
        assert 0.0 <= zone["density"] <= 1.0
        assert zone["status"] in ("LOW", "MEDIUM", "HIGH", "CRITICAL")


# ── Recommendation ────────────────────────────────────────────────────────────

def test_recommendation():
    r = client.get("/recommendation")
    assert r.status_code == 200
    data = r.json()

    assert "recommended_zone" in data
    assert "estimated_wait_minutes" in data
    assert "confidence" in data
    assert 0.0 <= data["confidence"] <= 1.0

    zone = data["recommended_zone"]
    assert "id" in zone
    assert "density" in zone


def test_recommendation_has_message():
    r = client.get("/recommendation")
    assert r.status_code == 200
    assert len(r.json()["message"]) > 10


# ── Simulation ────────────────────────────────────────────────────────────────

def test_simulate_default():
    r = client.post("/simulate", json={})
    assert r.status_code == 200
    data = r.json()
    assert data["ticks_applied"] == 1
    assert "new_state" in data


def test_simulate_multi_tick():
    r = client.post("/simulate", json={"tick_count": 3})
    assert r.status_code == 200
    assert r.json()["ticks_applied"] == 3


def test_simulate_with_surge():
    r = client.post("/simulate", json={
        "surge_zone": "EXIT_A",
        "surge_magnitude": 0.3,
        "tick_count": 1,
    })
    assert r.status_code == 200
    data = r.json()
    # EXIT_A should exist in updated zones
    zone_ids = [z["id"] for z in data["new_state"]["zones"]]
    assert "EXIT_A" in zone_ids


# ── Reset ─────────────────────────────────────────────────────────────────────

def test_reset():
    # First push a big surge
    client.post("/simulate", json={"surge_zone": "EXIT_B", "surge_magnitude": 0.6, "tick_count": 5})
    # Then reset
    r = client.post("/reset")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

    # Verify zones are back to defaults
    zones_r = client.get("/zones/")
    zones = zones_r.json()["zones"]
    exit_b = next(z for z in zones if z["id"] == "EXIT_B")
    assert abs(exit_b["density"] - 0.30) < 0.01   # default from sample_zones.json
