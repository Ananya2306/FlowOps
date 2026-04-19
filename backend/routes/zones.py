from fastapi import APIRouter
from datetime import datetime, timezone

from backend.services.crowd_simulation import get_all_zones
from backend.models.schema import VenueState, ZoneStatus, Coordinates

router = APIRouter(prefix="/zones", tags=["zones"])


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


@router.get("/", response_model=VenueState, summary="Get current crowd state for all exits")
async def get_zones():
    """Returns live crowd density, flow rate, and status for every exit zone."""
    meta, zones = get_all_zones()
    zone_models = [_zone_to_model(z) for z in zones.values()]
    total_crowd = sum(z.current_crowd for z in zone_models)

    return VenueState(
        venue_name=meta["name"],
        event=meta["event"],
        timestamp=datetime.now(timezone.utc),
        total_crowd=total_crowd,
        zones=zone_models,
    )
