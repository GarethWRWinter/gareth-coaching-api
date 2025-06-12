# main.py

from fastapi import FastAPI
from scripts import ride_database as db
from api.routes import router

# Create tables on startup
db.Base.metadata.create_all(bind=db.engine)

app = FastAPI()
app.include_router(router)
