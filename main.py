# main.py

from fastapi import FastAPI
from api.routes import router as ride_router  # ✅ Correctly imports the router

app = FastAPI()
app.include_router(ride_router, prefix="/api")
