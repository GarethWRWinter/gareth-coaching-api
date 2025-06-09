from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from scripts.ride_database import get_latest_ride, get_ride_history  # Update as needed
from scripts.sanitize import sanitize  # Recursive JSON-safe
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "🚴‍♂️ AI Cycling Coach API is alive!"}

@app.get("/latest-ride-data")
def latest_ride_data():
    try:
        latest_ride = get_latest_ride()
        if not latest_ride:
            raise HTTPException(status_code=404, detail="No ride found")

        response = {
            "ride_id": latest_ride.ride_id,
            "start_time": latest_ride.start_time,
            "duration_sec": latest_ride.duration_sec,
            "distance_km": latest_ride.distance_km,
            "avg_power": latest_ride.avg_power,
            "avg_hr": latest_ride.avg_hr,
            "avg_cadence": latest_ride.avg_cadence,
            "max_power": latest_ride.max_power,
            "max_hr": latest_ride.max_hr,
            "max_cadence": latest_ride.max_cadence,
            "total_work_kj": latest_ride.total_work_kj,
            "tss": latest_ride.tss,
            "left_right_balance": latest_ride.left_right_balance,
            "power_zone_times": latest_ride.power_zone_times,
            "normalized_power": latest_ride.normalized_power
        }

        logger.info(f"Latest ride: {response}")
        return sanitize(response)

    except Exception as e:
        logger.error(f"Error fetching latest ride: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ride-history")
def ride_history():
    try:
        rides = get_ride_history()
        logger.info(f"Fetched {len(rides)} rides.")
        return sanitize(rides)
    except Exception as e:
        logger.error(f"Error fetching ride history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# You can add other endpoints here if needed, like:
# @app.get("/trend-analysis")
# def trend_analysis():
#     ...

