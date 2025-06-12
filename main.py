from fastapi import FastAPI
from api.routes import router
from scripts.ride_database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(router)
