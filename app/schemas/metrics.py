from datetime import date

from pydantic import BaseModel


class PMCDataPoint(BaseModel):
    date: date
    tss: float
    ctl: float
    atl: float
    tsb: float
    ramp_rate: float | None = None


class PMCResponse(BaseModel):
    data: list[PMCDataPoint]
    current_ctl: float
    current_atl: float
    current_tsb: float


class ZoneBounds(BaseModel):
    name: str
    low: int
    high: int


class ZonesResponse(BaseModel):
    ftp: int
    power_zones: dict[str, ZoneBounds]
    hr_zones: dict[str, ZoneBounds] | None = None


class PowerProfilePoint(BaseModel):
    duration_seconds: int
    duration_label: str
    best_power: float
    watts_per_kg: float | None = None
    ride_id: str | None = None
    ride_date: date | None = None
    # All-time PB for comparison
    all_time_power: float | None = None
    all_time_watts_per_kg: float | None = None
    all_time_ride_date: date | None = None


class PowerProfileResponse(BaseModel):
    points: list[PowerProfilePoint]
    ftp: int
    w_per_kg: float | None = None
    days: int | None = None  # time window used (e.g. 90), None = all-time only


class RiderProfileScore(BaseModel):
    category: str  # "sprint", "anaerobic", "vo2max", "threshold", "endurance"
    label: str  # "Sprint (5s)", etc.
    score: float  # 0-100
    watts_per_kg: float | None = None


class FitnessSummaryResponse(BaseModel):
    ftp: int | None = None
    w_per_kg: float | None = None
    current_ctl: float
    current_atl: float
    current_tsb: float
    ramp_rate: float | None = None
    rider_type: str | None = None
    strengths: list[str] = []
    weaknesses: list[str] = []
    fitness_level: str  # "untrained", "fair", "moderate", "good", "very_good", "excellent"
    profile_scores: list[RiderProfileScore] = []


class FTPTestRequest(BaseModel):
    twenty_min_avg_power: float


class FTPHistoryPoint(BaseModel):
    date: date
    ftp: int
    source: str  # "test", "estimated", "manual"


class FTPHistoryResponse(BaseModel):
    history: list[FTPHistoryPoint]
    current_ftp: int | None = None


class WeeklyLoadPoint(BaseModel):
    week_start: date
    total_tss: float
    ride_count: int
    total_duration_seconds: int
    avg_intensity_factor: float | None = None


class WeeklyLoadResponse(BaseModel):
    weeks: list[WeeklyLoadPoint]


class RideZoneTime(BaseModel):
    zone: str
    zone_name: str
    low_watts: int
    high_watts: int
    seconds: int
    percentage: float


class RideZonesResponse(BaseModel):
    ftp: int
    zones: list[RideZoneTime]
    total_seconds: int
