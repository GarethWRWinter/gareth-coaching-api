from fastapi import FastAPI
from api.routes import router as ride_router

app = FastAPI()

@app.get("/")
def read_root():
    return {"status": "OK", "message": "Gareth Coaching API is live"}

app.include_router(ride_router)
