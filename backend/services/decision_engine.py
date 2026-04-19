"""
decision_engine.py
Analyzes current crowd state and produces actionable exit recommendations.
Uses a weighted scoring model (density + wait time + flow rate).
"""

from datetime import datetime, timezone
from typing import Optional
from backend.services.crowd_simulation import get_all_zones


# ── Scoring ───────────────────────────────────────────────────────────────────

def _score_zone(zone: dict) -> float:
    """
    Lower score = better exit.
    Weighted blend of:
      - density       (50%) — primary signal
      - wait_minutes  (30%) — queuing friction
      - flow_rate     (20%) — throughput capacity (inverted: higher flow = better)
    """
    max_flow = 700.0

    density_score   = zone["density"] * 0.50
    wait_score      = min(zone["estimated_wait_minutes"] / 30, 1.0) * 0.30
    flow_score      = (1 - zone["flow_rate"] / max_flow) * 0.20

    return round(density_score + wait_score + flow_score, 4)


def _confidence(best_score: float, second_score: float) -> float:
    """
    How confident are we in the recommendation?
    Gap between top-2 scores → normalized to [0.60, 0.99].
    """
    gap = max(second_score - best_score, 0)
    raw = min(gap / 0.30, 1.0)
    return round(0.60 + raw * 0.39, 2)


def _friendly_message(zone: dict, wait: float, saved: float) -> str:
    templates = {
        "LOW": (
            f"🟢 {zone['label']} ({zone['location']}) is clear — "
            f"move now for the fastest exit."
        ),
        "MEDIUM": (
            f"🟡 {zone['label']} ({zone['location']}) has moderate flow. "
            f"Estimated {wait:.0f} min — {saved:.0f} min faster than the worst route."
        ),
        "HIGH": (
            f"🟠 {zone['label']} is your best option despite some crowd. "
            f"Wait ~{wait:.0f} min — still {saved:.0f} min better than alternatives."
        ),
        "CRITICAL": (
            f"🔴 All exits are congested. {zone['label']} is marginally better. "
            f"Consider waiting 2–3 minutes before moving."
        ),
    }
    return templates.get(zone["status"], f"Head to {zone['label']}.")


# ── Public API ────────────────────────────────────────────────────────────────

def get_recommendation() -> dict:
    """Return the best exit zone + one alternative, with metadata."""
    _, zones = get_all_zones()
    zone_list = list(zones.values())

    scored = sorted(zone_list, key=_score_zone)

    best   = scored[0]
    second = scored[1] if len(scored) > 1 else None
    worst  = scored[-1]

    best_score   = _score_zone(best)
    second_score = _score_zone(second) if second else best_score + 0.05
    worst_wait   = worst["estimated_wait_minutes"]

    wait_saved = round(worst_wait - best["estimated_wait_minutes"], 1)
    confidence = _confidence(best_score, second_score)
    message    = _friendly_message(best, best["estimated_wait_minutes"], wait_saved)

    return {
        "recommended_zone": best,
        "alternative_zone": second,
        "estimated_wait_minutes": best["estimated_wait_minutes"],
        "time_saved_vs_worst": max(wait_saved, 0),
        "message": message,
        "confidence": confidence,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
