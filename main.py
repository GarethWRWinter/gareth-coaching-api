from fastapi import FastAPI
from api.routes import router as ride_router  # Make sure this file exists

app = FastAPI(
    title="Gareth Coaching API",
    description="An API to process and analyze cycling ride data from Dropbox",
    version="1.0.0",
)

@app.get("/")
def health_check():
    return {"status": "OK", "message": "Gareth Coaching API is live"}

# Include the route from api/routes.py
app.include_router(ride_router, prefix="/api")
