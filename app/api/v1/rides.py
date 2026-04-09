from datetime import datetime

from fastapi import APIRouter, Depends, File, Query, UploadFile
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_user
from app.core.exceptions import BadRequestException, NotFoundException
from app.database import get_db
from app.models.user import User
from app.models.segment import SegmentEffort, StravaSegment
from app.schemas.ride import (
    PowerCurveResponse,
    RideDataResponse,
    RideListResponse,
    RideRecordRequest,
    RideResponse,
)
from app.schemas.segment import RideSegmentsResponse, SegmentEffortResponse
from app.services import ride_service
from app.services.metrics_service import recalculate_from_date

router = APIRouter(prefix="/rides", tags=["rides"])


@router.post("/upload", response_model=RideResponse, status_code=201)
def upload_fit_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Upload a FIT file, parse it, create ride with calculated metrics."""
    if not file.filename or not file.filename.lower().endswith(".fit"):
        raise BadRequestException(detail="File must be a .fit file")

    file_bytes = file.file.read()
    if len(file_bytes) == 0:
        raise BadRequestException(detail="File is empty")

    if len(file_bytes) > 50 * 1024 * 1024:  # 50MB limit
        raise BadRequestException(detail="File too large (max 50MB)")

    ride = ride_service.create_ride_from_fit(
        db, current_user, file_bytes, filename=file.filename
    )

    # Recalculate PMC from ride date
    if ride.tss and ride.ride_date:
        recalculate_from_date(db, current_user.id, ride.ride_date.date())

    return ride


@router.post("/record", response_model=RideResponse, status_code=201)
def record_ride(
    body: RideRecordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Save an in-app workout recording (from workout player)."""
    if not body.data_points:
        raise BadRequestException(detail="No data points provided")

    data_dicts = [dp.model_dump() for dp in body.data_points]
    ride = ride_service.create_ride_from_recording(
        db, current_user, body.title, body.ride_date,
        data_dicts, body.workout_id
    )

    if ride.tss and ride.ride_date:
        recalculate_from_date(db, current_user.id, ride.ride_date.date())

    return ride


@router.get("", response_model=RideListResponse)
def list_rides(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List rides with pagination and optional date filtering."""
    rides, total = ride_service.get_rides(
        db, current_user.id, page, per_page, start_date, end_date
    )
    return RideListResponse(
        rides=[RideResponse.model_validate(r) for r in rides],
        total=total, page=page, per_page=per_page,
    )


@router.get("/{ride_id}", response_model=RideResponse)
def get_ride(
    ride_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a single ride summary."""
    ride = ride_service.get_ride(db, ride_id, current_user.id)
    if not ride:
        raise NotFoundException(detail="Ride not found")
    return ride


@router.get("/{ride_id}/data", response_model=RideDataResponse)
def get_ride_data(
    ride_id: str,
    resolution: str = Query("5s", pattern="^(full|5s|30s)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get time-series data for a ride (supports downsampling)."""
    ride = ride_service.get_ride(db, ride_id, current_user.id)
    if not ride:
        raise NotFoundException(detail="Ride not found")

    data_points = ride_service.get_ride_data(db, ride_id, resolution)
    return RideDataResponse(
        ride_id=ride_id,
        resolution=resolution,
        data_points=data_points,
        total_points=len(data_points),
    )


@router.get("/{ride_id}/power-curve", response_model=PowerCurveResponse)
def get_power_curve(
    ride_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get best-effort power curve for a single ride."""
    ride = ride_service.get_ride(db, ride_id, current_user.id)
    if not ride:
        raise NotFoundException(detail="Ride not found")

    points = ride_service.get_ride_power_curve(db, ride_id)
    return PowerCurveResponse(ride_id=ride_id, points=points)


@router.get("/{ride_id}/segments", response_model=RideSegmentsResponse)
def get_ride_segments(
    ride_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get segment efforts, achievements, and social data for a ride."""
    ride = ride_service.get_ride(db, ride_id, current_user.id)
    if not ride:
        raise NotFoundException(detail="Ride not found")

    efforts = (
        db.query(SegmentEffort, StravaSegment)
        .join(StravaSegment, SegmentEffort.segment_id == StravaSegment.id)
        .filter(SegmentEffort.ride_id == ride_id)
        .order_by(SegmentEffort.elapsed_time_seconds.desc())
        .all()
    )

    segment_efforts = [
        SegmentEffortResponse(
            id=effort.id,
            segment_name=segment.name,
            distance_meters=segment.distance_meters,
            average_grade=segment.average_grade,
            climb_category=segment.climb_category,
            elapsed_time_seconds=effort.elapsed_time_seconds,
            moving_time_seconds=effort.moving_time_seconds,
            average_watts=effort.average_watts,
            max_watts=effort.max_watts,
            average_hr=effort.average_hr,
            max_hr=effort.max_hr,
            pr_rank=effort.pr_rank,
            kom_rank=effort.kom_rank,
            achievement_type=effort.achievement_type,
        )
        for effort, segment in efforts
    ]

    return RideSegmentsResponse(
        ride_id=ride_id,
        achievement_count=ride.achievement_count,
        pr_count=ride.pr_count,
        kudos_count=ride.kudos_count,
        segment_efforts=segment_efforts,
    )
