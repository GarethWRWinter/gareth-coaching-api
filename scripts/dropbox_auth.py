import os
import requests
import logging

logger = logging.getLogger(__name__)

DROPBOX_REFRESH_TOKEN = os.getenv("DROPBOX_REFRESH_TOKEN")
DROPBOX_APP_KEY = os.getenv("DROPBOX_APP_KEY")
DROPBOX_APP_SECRET = os.getenv("DROPBOX_APP_SECRET")

def refresh_dropbox_token():
    if not DROPBOX_REFRESH_TOKEN or not DROPBOX_APP_KEY or not DROPBOX_APP_SECRET:
        raise EnvironmentError("Missing Dropbox app key, secret, or refresh token.")

    url = "https://api.dropboxapi.com/oauth2/token"
    data = {
        "grant_type": "refresh_token",
        "refresh_token": DROPBOX_REFRESH_TOKEN
    }

    response = requests.post(url, data=data, auth=(DROPBOX_APP_KEY, DROPBOX_APP_SECRET))
    if response.status_code == 200:
        access_token = response.json()["access_token"]
        logger.info("Dropbox access token refreshed.")
        return access_token
    else:
        logger.error(f"Failed to refresh Dropbox token: {response.text}")
        raise RuntimeError("Dropbox token refresh failed.")
