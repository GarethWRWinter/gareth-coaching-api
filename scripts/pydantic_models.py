
from pydantic import BaseModel
from typing import Dict, Any

class RideSummary(BaseModel):
    date: str
    total_distance_km: float
    duration_minutes: float
    avg_power: float
    avg_heart_rate: float
    time_in_zones: Dict[str, Any]
    pedal_smoothness: float | None = None
    notes: str | None = None
