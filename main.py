from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from scripts.ride_database import get_all_rides, get_ride
from scripts.ftp_detection import detect_and_update_ftp
from scripts.trend_analysis import calculate_trend_metrics
from scripts.rolling_power import calculate_rolling_power_trends

app = FastAPI()

@app.get("/")
def root():
    return {"message": "API is running!"}

@app.get("/latest-ride-data")
def latest_ride_data():
    rides = get_all_rides()
    if not rides:
        raise HTTPException(status_code=404, detail="No rides found.")
    latest_ride = rides[0]
    return JSONResponse(content=latest_ride.__dict__)

@app.get("/ride-history")
def ride_history():
    rides = get_all_rides()
    if not rides:
        raise HTTPException(status_code=404, detail="No rides found.")
    return JSONResponse(content=[ride.__dict__ for ride in rides])

@app.get("/ftp-update")
def ftp_update():
    return detect_and_update_ftp()

@app.get("/trend-analysis")
def trend_analysis():
    return calculate_trend_metrics()

@app.get("/power-trends")
def power_trends():
    return calculate_rolling_power_trends()
