from fastapi import FastAPI
from api.routes import router as ride_router

app = FastAPI(
    title="Gareth Coaching API",
    description="API to fetch and analyze cycling ride data from Dropbox .FIT files",
    version="1.0.0",
    servers=[
        {"url": "https://gareth-coaching-api.onrender.com"}
    ]
)

app.include_router(ride_router)
