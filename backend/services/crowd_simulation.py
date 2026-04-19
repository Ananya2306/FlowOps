"""
crowd_simulation.py
Simulates realistic crowd density changes over time.
Includes time-based spikes, surge events, and decay/recovery behavior.
"""

import random
import json
import math
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional

# ── Internal state (in-memory; Redis would replace this in prod) ──────────────
_zones: dict = {}
_venue_meta: dict = {}


def _load_initial_state() -> None:
    """Bootstrap zone data from sample_zones.json on first call."""
    global _zones, _venue_meta
    data_path = Path(__file__).parent.parent.parent / "data" / "sample_zones.json"
    with open(data_path) as f:
        raw = json.load(f)

    _venue_meta = raw["venue"]
    _zones = {z["id"]: dict(z) for z in raw["zones"]}
    _compute_wait_times()


def _compute_wait_times() -> None:
    """Derived field: estimated wait (minutes) from density + flow_rate."""
    for zone in _zones.values():
        crowd = zone["current_crowd"]
        flow  = max(zone["flow_rate"], 1)
        # Simple queuing model: wait ≈ (crowd in queue) / flow_rate
        zone["estimated_wait_minutes"] = round(crowd / flow, 1)


def _status_from_density(density: float) -> str:
    if density < 0.40:
        return "LOW"
    elif density < 0.60:
        return "MEDIUM"
    elif density < 0.80:
        return "HIGH"
    else:
        return "CRITICAL"


# ── Public API ────────────────────────────────────────────────────────────────

def get_all_zones() -> tuple[dict, dict]:
    """Return (venue_meta, zones_dict). Lazy-loads on first call."""
    if not _zones:
        _load_initial_state()
    return _venue_meta, dict(_zones)


def tick(surge_zone: Optional[str] = None, surge_magnitude: float = 0.20) -> list[str]:
    """
    Advance simulation by one time step.

    - Each zone drifts randomly (±0.08 density)
    - Denser zones drain faster (natural crowd dispersal)
    - Optional surge injects a crowd spike into one zone
    - Crowd count + flow_rate update accordingly

    Returns list of updated zone IDs.
    """
    if not _zones:
        _load_initial_state()

    updated = []

    for zone_id, zone in _zones.items():
        d = zone["density"]

        # Natural drift: busier zones drain faster
        drift = random.uniform(-0.08, 0.06) - (d * 0.05)

        # Surge injection
        if zone_id == surge_zone:
            drift += surge_magnitude

        # Time-of-event pattern: add a sine-wave pulse so it feels alive
        t = datetime.now(timezone.utc).timestamp()
        pulse = 0.02 * math.sin(t / 60 + hash(zone_id) % 10)
        drift += pulse

        new_density = max(0.0, min(1.0, d + drift))
        zone["density"] = round(new_density, 3)
        zone["current_crowd"] = int(new_density * zone["capacity"])

        # Flow rate inversely proportional to density (more crowd → slower flow)
        base_flow = 700
        zone["flow_rate"] = max(100, int(base_flow * (1 - new_density * 0.7)))
        zone["status"] = _status_from_density(new_density)
        updated.append(zone_id)

    _compute_wait_times()
    return updated


def reset_to_default() -> None:
    """Hard-reset all zones to file defaults."""
    global _zones, _venue_meta
    _zones = {}
    _venue_meta = {}
    _load_initial_state()
