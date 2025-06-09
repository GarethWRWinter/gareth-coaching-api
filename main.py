from fastapi import FastAPI
from scripts.ride_database import get_latest_ride, get_ride_history
from scripts.trend_analysis import calculate_trend_metrics
from scripts.rolling_power import get_power_trends
from scripts.ftp_detection import detect_ftp_change

app = FastAPI()


@app.get("/latest-ride-data")
def latest_ride_data():
    return get_latest_ride()


@app.get("/ride-history")
def ride_history():
    return get_ride_history()


@app.get("/trend-analysis")
def trend_analysis():
    return calculate_trend_metrics()


@app.get("/power-trends")
def power_trends():
    return get_power_trends()


@app.get("/ftp-update")
def ftp_update():
    return detect_ftp_change()
