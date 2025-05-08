# api/routes.py

from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def root():
    return {
        "status": "OK",
        "message": "Gareth Coaching API is live"
    }
