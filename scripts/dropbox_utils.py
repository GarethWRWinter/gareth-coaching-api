import os
import requests
from dotenv import load_dotenv

load_dotenv()

DROPBOX_APP_KEY = os.getenv("DROPBOX_APP_KEY")
DROPBOX_APP_SECRET = os.getenv("DROPBOX_APP_SECRET")
DROPBOX_REFRESH_TOKEN = os.getenv("DROPBOX_REFRESH_TOKEN")

def refresh_dropbox_token() -> str:
    if not all([DROPBOX_APP_KEY, DROPBOX_APP_SECRET, DROPBOX_REFRESH_TOKEN]):
        raise Exception("Missing Dropbox credentials in environment variables.")

    response = requests.post(
        "https://api.dropbox.com/oauth2/token",
        data={
            "grant_type": "refresh_token",
            "refresh_token": DROPBOX_REFRESH_TOKEN,
            "client_id": DROPBOX_APP_KEY,
            "client_secret": DROPBOX_APP_SECRET,
        },
    )

    if response.status_code != 200:
        raise Exception(f"Failed to refresh token: {response.text}")

    new_token = response.json()["access_token"]
    os.environ["DROPBOX_TOKEN"] = new_token  # Update token in runtime
    return new_token
