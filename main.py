from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router as api_router
import logging

app = FastAPI()

# Optional: Enable CORS (for local testing or web frontend access)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routing
app.include_router(api_router)

# Startup message
@app.on_event("startup")
def startup_event():
    logging.info("Starting FastAPI app...")
