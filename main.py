from fastapi import FastAPI
from api.routes import router as ride_router

app = FastAPI(
    title="Gareth Coaching API",
    version="1.0.0",
)

app.include_router(ride_router)
