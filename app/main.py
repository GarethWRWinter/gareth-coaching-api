import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.config import settings
from app.services.auto_sync import start_auto_sync, stop_auto_sync

logger = logging.getLogger(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown lifecycle."""
    # --- Startup ---
    sync_interval = settings.dropbox_sync_interval
    if sync_interval > 0:
        start_auto_sync(interval=sync_interval)
        logger.info("Dropbox auto-sync enabled (every %ds)", sync_interval)
    else:
        logger.info("Dropbox auto-sync disabled (interval=0)")
    yield
    # --- Shutdown ---
    stop_auto_sync()
    logger.info("App shutdown complete")


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="AI-powered cycling coach with training plans, ride analytics, and conversational coaching",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
def health_check():
    return {"status": "healthy"}
