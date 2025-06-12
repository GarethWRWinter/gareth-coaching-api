from fastapi import APIRouter, HTTPException, Query
from scripts.ride_processor import process_latest_fit_file, get_all_rides
from pydantic import BaseModel

router = APIRouter()

# GET /latest-ride-data?ftp=308
@router.get("/latest-ride-data")
async def latest_ride_data(ftp: float = Query(..., gt=0, description="Functional Threshold Power")):
    try:
        data = process_latest_fit_file(ftp)
        return data
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process latest ride: {e}")

# GET /ride-history
@router.get("/ride-history")
async def ride_history():
    try:
        return {"rides": get_all_rides()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch ride history: {e}")

# PUT /ftp
class UpdateFTPRequest(BaseModel):
    new_ftp: float

_current_ftp = 308.0

@router.put("/ftp")
async def update_ftp(req: UpdateFTPRequest):
    global _current_ftp
    prev = _current_ftp
    _current_ftp = req.new_ftp
    return {"previous_ftp": prev, "new_ftp": _current_ftp}
