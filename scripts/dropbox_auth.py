# ✅ scripts/dropbox_auth.py

import os
import requests
from dotenv import load_dotenv

load_dotenv()

DROPBOX_REFRESH_TOKEN = os.getenv("DROPBOX_REFRESH_TOKEN")
DROPBOX_APP_KEY = os.getenv("DROPBOX_APP_KEY")
DROPBOX_APP_SECRET = os.getenv("DROPBOX_APP_SECRET")

def get_valid_access_token() -> str:
    """
    Returns a new short-lived Dropbox access token using the refresh token.
    """
    token_url = "https://api.dropbox.com/oauth2/token"
    data = {
        "refresh_token": DROPBOX_REFRESH_TOKEN,
        "grant_type": "refresh_token",
        "client_id": DROPBOX_APP_KEY,
        "client_secret": DROPBOX_APP_SECRET,
    }

    response = requests.post(token_url, data=data)
    if response.status_code != 200:
        raise Exception(f"Dropbox token refresh failed: {response.text}")
    
    access_token = response.json().get("access_token")
    if not access_token:
        raise Exception("No access token returned from Dropbox.")
    
    return access_token
