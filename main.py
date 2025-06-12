# main.py

from fastapi import FastAPI
from api.routes import router
from scripts.ride_database import init_db

app = FastAPI()
app.include_router(router)

# Ensure DB tables exist
init_db()
