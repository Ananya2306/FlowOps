"""
helpers.py
Shared utility functions used across backend services.
"""

from datetime import datetime, timezone


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def density_to_color(density: float) -> str:
    """Return a hex color representing crowd density for map overlays."""
    if density < 0.40:
        return "#22c55e"   # green
    elif density < 0.60:
        return "#eab308"   # yellow
    elif density < 0.80:
        return "#f97316"   # orange
    else:
        return "#ef4444"   # red


def format_wait(minutes: float) -> str:
    if minutes < 1:
        return "< 1 min"
    elif minutes < 60:
        return f"{minutes:.0f} min"
    else:
        hours = int(minutes // 60)
        mins  = int(minutes % 60)
        return f"{hours}h {mins}m"
