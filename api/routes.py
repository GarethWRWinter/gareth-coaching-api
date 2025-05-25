from fastapi import APIRouter, HTTPException
from scripts.fetch_and_parse import process_latest_fit_file
from scripts.ride_database import get_all_rides, get_ride_by_id, store_ride
from scripts.sanitize import sanitize
from scripts.trend_analysis import generate_trend_analysis

router = APIRouter()


@router.get("/latest-ride-data")
async def get_latest_ride_data():
    try:
        summary, full_data, *_ = process_latest_fit_file()
        store_ride(summary, full_data)
        return sanitize(summary)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process latest ride: {str(e)}")


@router.get("/ride-history")
async def get_ride_history():
    try:
        rides = get_all_rides()
        return {"rides": sanitize(rides)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch ride history: {str(e)}")


@router.get("/ride/{ride_id}")
async def get_ride_by_id_route(ride_id: str):
    try:
        ride = get_ride_by_id(ride_id)
        if ride:
            return sanitize(ride)
        else:
            raise HTTPException(status_code=404, detail="Ride not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch ride: {str(e)}")


@router.get("/trend-analysis")
async def get_trend_analysis():
    try:
        trends = generate_trend_analysis()
        return sanitize(trends)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate trend analysis: {str(e)}")
