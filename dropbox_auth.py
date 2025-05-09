# dropbox_auth.py

import os
import requests
from dotenv import load_dotenv

load_dotenv()

DROPBOX_APP_KEY = os.getenv("DROPBOX_APP_KEY")
DROPBOX_APP_SECRET = os.getenv("DROPBOX_APP_SECRET")
DROPBOX_REFRESH_TOKEN = os.getenv("DROPBOX_REFRESH_TOKEN")

def refresh_dropbox_token():
    token_url = "https://api.dropbox.com/oauth2/token"

    response = requests.post(
        token_url,
        data={
            "grant_type": "refresh_token",
            "refresh_token": DROPBOX_REFRESH_TOKEN,
            "client_id": DROPBOX_APP_KEY,
            "client_secret": DROPBOX_APP_SECRET,
        },
    )

    if response.status_code != 200:
        raise Exception(f"Dropbox token refresh failed: {response.text}")

    new_token = response.json()["access_token"]
    return new_token
