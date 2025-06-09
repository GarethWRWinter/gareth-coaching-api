# main.py
from fastapi import FastAPI
from api.routes import router

app = FastAPI()

# Include the router from the API module
app.include_router(router)

# Optional: add a root health check (e.g., GET /)
@app.get("/")
def read_root():
    return {"status": "API is live"}
