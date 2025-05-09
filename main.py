import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from dropbox_auth import refresh_dropbox_token
from api.routes import router as api_router

load_dotenv()

app = FastAPI()

# Optional CORS if needed for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    print("Starting FastAPI app...")
    try:
        access_token = refresh_dropbox_token()
        print("Dropbox token refreshed successfully.")
    except Exception as e:
        print(f"Failed to refresh Dropbox token at startup: {e}")

# Attach API routes
app.include_router(api_router)

@app.get("/")
def root():
    return {"message": "Cycling Coach API is live"}
