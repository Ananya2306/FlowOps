from fastapi import APIRouter
from datetime import datetime, timezone

from backend.services.decision_engine import get_recommendation
from backend.services.crowd_simulation import tick, get_all_zones, reset_to_default
from backend.models.schema import (
    Recommendation, SimulationRequest, SimulationResponse, VenueState, ZoneStatus, Coordinates
)

router = APIRouter(tags=["decisions"])


def _zone_to_model(z: dict) -> ZoneStatus:
    return ZoneStatus(
        id=z["id"],
        label=z["label"],
        location=z["location"],
        capacity=z["capacity"],
        current_crowd=z["current_crowd"],
        density=z["density"],
        flow_rate=z["flow_rate"],
        status=z["status"],
        coordinates=Coordinates(**z["coordinates"]),
        estimated_wait_minutes=z.get("estimated_wait_minutes"),
    )


@router.get("/recommendation", response_model=Recommendation, summary="Get best exit recommendation")
async def recommend():
    """
    Analyzes all zones and returns the optimal exit route with estimated wait,
    time saved vs worst route, and a human-friendly message.
    """
    rec = get_recommendation()
    return Recommendation(
        recommended_zone=_zone_to_model(rec["recommended_zone"]),
        alternative_zone=_zone_to_model(rec["alternative_zone"]) if rec["alternative_zone"] else None,
        estimated_wait_minutes=rec["estimated_wait_minutes"],
        time_saved_vs_worst=rec["time_saved_vs_worst"],
        message=rec["message"],
        confidence=rec["confidence"],
        generated_at=datetime.fromisoformat(rec["generated_at"]),
    )


@router.post("/simulate", response_model=SimulationResponse, summary="Advance simulation tick")
async def simulate(req: SimulationRequest):
    """
    Advances the crowd simulation by N ticks. Optionally injects a surge
    into a specific zone. Use this to demo dynamic crowd behavior.
    """
    all_updated = []
    for _ in range(req.tick_count):
        updated = tick(surge_zone=req.surge_zone, surge_magnitude=req.surge_magnitude)
        all_updated.extend(updated)

    meta, zones = get_all_zones()
    zone_models = [_zone_to_model(z) for z in zones.values()]
    total_crowd = sum(z.current_crowd for z in zone_models)

    return SimulationResponse(
        ticks_applied=req.tick_count,
        zones_updated=list(set(all_updated)),
        new_state=VenueState(
            venue_name=meta["name"],
            event=meta["event"],
            timestamp=datetime.now(timezone.utc),
            total_crowd=total_crowd,
            zones=zone_models,
        ),
    )


@router.post("/reset", summary="Reset simulation to default state")
async def reset():
    """Resets all zone data back to the initial sample_zones.json values."""
    reset_to_default()
    return {"status": "ok", "message": "Simulation reset to default state."}
