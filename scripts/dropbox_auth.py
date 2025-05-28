import os
import requests
from dotenv import load_dotenv

load_dotenv()

DROPBOX_APP_KEY = os.getenv("DROPBOX_APP_KEY")
DROPBOX_APP_SECRET = os.getenv("DROPBOX_APP_SECRET")
DROPBOX_REFRESH_TOKEN = os.getenv("DROPBOX_REFRESH_TOKEN")


def refresh_dropbox_token() -> str:
    """
    Refreshes the Dropbox access token using the refresh token.
    Returns the new access token.
    """
    if not all([DROPBOX_APP_KEY, DROPBOX_APP_SECRET, DROPBOX_REFRESH_TOKEN]):
        raise EnvironmentError("Missing Dropbox credentials in environment variables.")

    url = "https://api.dropboxapi.com/oauth2/token"
    auth = (DROPBOX_APP_KEY, DROPBOX_APP_SECRET)
    data = {
        "refresh_token": DROPBOX_REFRESH_TOKEN,
        "grant_type": "refresh_token",
    }

    response = requests.post(url, auth=auth, data=data)
    if response.status_code != 200:
        raise RuntimeError(f"Failed to refresh Dropbox token: {response.text}")

    access_token = response.json().get("access_token")
    if not access_token:
        raise ValueError("Access token not found in Dropbox response.")

    return access_token
