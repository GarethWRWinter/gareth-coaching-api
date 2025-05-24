import os
import sys
import logging
from fastapi import FastAPI
from dotenv import load_dotenv
from api.routes import router as api_router
from scripts.ride_database import initialize_database  # ✅ added

# Allow relative imports to work locally and in production
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Required environment variables
REQUIRED_ENV_VARS = [
    "DROPBOX_APP_KEY",
    "DROPBOX_APP_SECRET",
    "DROPBOX_REFRESH_TOKEN",
    "DROPBOX_TOKEN",
    "DROPBOX_FOLDER"
]

for var in REQUIRED_ENV_VARS:
    if not os.getenv(var):
        logger.warning(f"Environment variable {var} is not set!")

# ✅ Ensure DB is initialized
initialize_database()

# FastAPI app
app = FastAPI(
    title="AI Cycling Coach API",
    description="Backend API for analyzing and coaching cycling performance based on FIT files.",
    version="1.0.0"
)

# Register API routes
app.include_router(api_router)
