# main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from scripts.ride_database import get_latest_ride, get_ride_history
from scripts.trend_analysis import calculate_trend_metrics
from scripts.rolling_power import calculate_rolling_power_trends
from scripts.ftp_detection import detect_ftp_change  # Assuming main function

from scripts.sanitize import sanitize

app = FastAPI()

# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/latest-ride-data")
def latest_ride_data():
    ride = get_latest_ride()
    return sanitize(ride)

@app.get("/ride-history")
def ride_history():
    rides = get_ride_history()
    return sanitize(rides)

@app.get("/trend-analysis")
def trend_analysis():
    data = calculate_trend_metrics()
    return sanitize(data)

@app.get("/power-trends")
def power_trends():
    data = calculate_rolling_power_trends()
    return sanitize(data)

@app.get("/ftp-update")
def ftp_update():
    data = detect_ftp_change()
    return sanitize(data)
