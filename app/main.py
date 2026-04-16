import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.config import settings
from app.services.auto_sync import start_auto_sync, stop_auto_sync
from app.services.strava_service import resume_incomplete_backfills

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

    # Resume any Strava backfills that were interrupted by a previous restart.
    # Runs in background so we don't block startup.
    asyncio.create_task(resume_incomplete_backfills())
    logger.info("Scheduled Strava backfill resume check")

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

origins = list(settings.cors_origins)
if settings.frontend_url:
    origins.append(settings.frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
def health_check():
    return {"status": "healthy"}
