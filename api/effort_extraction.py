from fastapi import APIRouter, HTTPException, Query
from scripts.ride_database import get_ride_by_id
from fastapi.responses import JSONResponse

router = APIRouter()

@router.get("/ride/{ride_id}/efforts")
def get_power_efforts(
    ride_id: str,
    min_power: int = Query(300, description="Minimum power threshold in watts"),
    min_duration: int = Query(60, description="Minimum effort duration in seconds"),
):
    data = get_ride_by_id(ride_id)
    if not data:
        raise HTTPException(status_code=404, detail="Ride not found")

    records = data.get("full_data", [])
    efforts = []
    current_effort = []

    for record in records:
        if record.get("power", 0) >= min_power:
            current_effort.append(record)
        else:
            if len(current_effort) >= min_duration:
                efforts.append(current_effort)
            current_effort = []

    if len(current_effort) >= min_duration:
        efforts.append(current_effort)

    result = [
        {
            "start_time": effort[0]["timestamp"],
            "end_time": effort[-1]["timestamp"],
            "duration": len(effort),
            "avg_power": round(sum(e["power"] for e in effort) / len(effort), 1)
        }
        for effort in efforts
    ]

    return JSONResponse(content=result)
