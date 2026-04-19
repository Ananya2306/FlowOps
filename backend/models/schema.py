from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime


class Coordinates(BaseModel):
    x: float = Field(..., ge=0.0, le=1.0, description="Normalized X position (0–1)")
    y: float = Field(..., ge=0.0, le=1.0, description="Normalized Y position (0–1)")


class ZoneStatus(BaseModel):
    id: str
    label: str
    location: str
    capacity: int
    current_crowd: int
    density: float = Field(..., ge=0.0, le=1.0)
    flow_rate: int = Field(..., description="People per minute exiting")
    status: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    coordinates: Coordinates
    estimated_wait_minutes: Optional[float] = None


class VenueState(BaseModel):
    venue_name: str
    event: str
    timestamp: datetime
    total_crowd: int
    zones: list[ZoneStatus]


class Recommendation(BaseModel):
    recommended_zone: ZoneStatus
    alternative_zone: Optional[ZoneStatus]
    estimated_wait_minutes: float
    time_saved_vs_worst: float
    message: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    generated_at: datetime


class SimulationRequest(BaseModel):
    surge_zone: Optional[str] = None
    surge_magnitude: float = Field(default=0.2, ge=0.0, le=1.0)
    tick_count: int = Field(default=1, ge=1, le=10)


class SimulationResponse(BaseModel):
    ticks_applied: int
    zones_updated: list[str]
    new_state: VenueState


class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: datetime
