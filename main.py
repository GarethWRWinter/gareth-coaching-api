from fastapi import FastAPI
from api.routes import router

app = FastAPI(
    title="Gareth's Cycling Coach API",
    description="World-class, data-driven cycling coaching API for Gareth's performance insights: live ride data, history, power trends, FTP updates, and training load.",
    version="1.0.0",
)

app.include_router(router)
