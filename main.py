from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import fetch_latest_ride  # Add other routes as needed

app = FastAPI(
    title="Gareth Coaching API",
    description="World-class cycling coach backend.",
    version="1.0.0"
)

# Allow CORS for GPT access or local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can tighten this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(fetch_latest_ride.router)

@app.get("/")
def root():
    return {"message": "Gareth Coaching API is running."}
