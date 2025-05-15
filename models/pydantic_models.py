from pydantic import BaseModel
from typing import Dict, List, Any

class RideSummary(BaseModel):
    date: str
    duration_sec: float
    avg_power: float
    max_power: float
    avg_hr: float
    max_hr: float
    avg_cadence: float
    max_cadence: float
    distance_km: float
    total_work_kj: float
    time_in_zones: Dict[str, int]

class RideDataResponse(BaseModel):
    raw: List[Dict[str, Any]]
    summary: RideSummary
