from pydantic import BaseModel
from typing import Dict, Any

class RideSummary(BaseModel):
    ride_id: str  # ✅ this was missing
    date: str
    duration_sec: int
    avg_power: float
    max_power: int
    avg_hr: float
    max_hr: int
    avg_cadence: float
    max_cadence: int
    distance_km: float
    total_work_kj: float
    time_in_zones: Dict[str, Any]
    full_data: Dict[str, Any]
