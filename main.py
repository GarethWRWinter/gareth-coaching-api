# main.py

from fastapi import FastAPI
from api.routes import router
import scripts.ride_database as db

db.Base.metadata.create_all(bind=db.engine)

app = FastAPI()
app.include_router(router)
