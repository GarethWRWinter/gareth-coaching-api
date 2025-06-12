# main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router

app = FastAPI(
    title="Gareth's Cycling Coach API",
    version="1.0.0",
    description=(
        "World-class, data-driven cycling coaching API for Gareth's performance insights: "
        "live ride data, history, power trends, FTP updates, and training load."
    ),
    openapi_version="3.1.0"
)

# Allow CORS for GPTs or web clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# Include API router
app.include_router(router)
