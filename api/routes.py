from fastapi import FastAPI
from api.routes import router as ride_router

app = FastAPI()

@app.get("/")
def root():
    return {"status": "API is running"}

app.include_router(ride_router)

