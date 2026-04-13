from fastapi import APIRouter

from app.api.v1 import auth, chat, coach_insights, exports, goals, integrations, metrics, onboarding, rides, training, users
from app.api.v1.dropbox import router as dropbox_router

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(rides.router)
api_router.include_router(metrics.router)
api_router.include_router(onboarding.router)
api_router.include_router(goals.router)
api_router.include_router(training.router)
api_router.include_router(exports.router)
api_router.include_router(integrations.router)
api_router.include_router(chat.router)
api_router.include_router(coach_insights.router)
api_router.include_router(dropbox_router)
