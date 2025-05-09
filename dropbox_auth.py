# dropbox_auth.py

import os
import requests

DROPBOX_APP_KEY = os.getenv("DROPBOX_APP_KEY")
DROPBOX_APP_SECRET = os.getenv("DROPBOX_APP_SECRET")
DROPBOX_REFRESH_TOKEN = os.getenv("DROPBOX_REFRESH_TOKEN")

def refresh_dropbox_token():
    url = "https://api.dropbox.com/oauth2/token"
    data = {
        "grant_type": "refresh_token",
        "refresh_token": DROPBOX_REFRESH_TOKEN,
        "client_id": DROPBOX_APP_KEY,
        "client_secret": DROPBOX_APP_SECRET,
    }
    response = requests.post(url, data=data)
    response.raise_for_status()
    access_token = response.json().get("access_token")
    os.environ["DROPBOX_TOKEN"] = access_token
    return access_token

def get_dropbox_access_token():
    # Always refresh on-demand
    return refresh_dropbox_token()
