from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router as api_router

app = FastAPI(
    title="Gareth's AI Cycling Coach",
    description="A FastAPI backend for analyzing Wahoo .FIT files and delivering training insights.",
    version="2.0.0",
)

# Allow all CORS for now — restrict later if needed
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
