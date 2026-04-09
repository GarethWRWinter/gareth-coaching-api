from pydantic import BaseModel


class SegmentEffortResponse(BaseModel):
    id: str
    segment_name: str
    distance_meters: float | None = None
    average_grade: float | None = None
    climb_category: int | None = None
    elapsed_time_seconds: int
    moving_time_seconds: int | None = None
    average_watts: float | None = None
    max_watts: int | None = None
    average_hr: float | None = None
    max_hr: int | None = None
    pr_rank: int | None = None
    kom_rank: int | None = None
    achievement_type: str | None = None


class RideSegmentsResponse(BaseModel):
    ride_id: str
    achievement_count: int | None = None
    pr_count: int | None = None
    kudos_count: int | None = None
    segment_efforts: list[SegmentEffortResponse]
