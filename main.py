# main.py

import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from api.routes import router
from dropbox_auth import refresh_dropbox_token

load_dotenv()

app = FastAPI()

# Include routes
app.include_router(router)

@app.get("/")
def root():
    return {"status": "OK"}

@app.get("/latest-ride-data")
def get_latest_ride_data():
    try:
        print("Refreshing Dropbox token...")
        access_token = refresh_dropbox_token()
        from scripts.save_latest_ride_to_db import save_latest_ride_to_db
        result = save_latest_ride_to_db(access_token)
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
