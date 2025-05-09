import os
import requests

DROPBOX_APP_KEY = os.environ.get("DROPBOX_APP_KEY")
DROPBOX_APP_SECRET = os.environ.get("DROPBOX_APP_SECRET")
DROPBOX_REFRESH_TOKEN = os.environ.get("DROPBOX_REFRESH_TOKEN")


def refresh_dropbox_token():
    if not DROPBOX_REFRESH_TOKEN or not DROPBOX_APP_KEY or not DROPBOX_APP_SECRET:
        raise ValueError("Missing Dropbox environment variables.")

    response = requests.post(
        "https://api.dropbox.com/oauth2/token",
        data={
            "grant_type": "refresh_token",
            "refresh_token": DROPBOX_REFRESH_TOKEN,
        },
        auth=(DROPBOX_APP_KEY, DROPBOX_APP_SECRET),
    )

    if response.status_code != 200:
        raise Exception(f"Failed to refresh token: {response.text}")

    access_token = response.json().get("access_token")
    if not access_token:
        raise Exception("No access token in Dropbox response.")

    os.environ["DROPBOX_TOKEN"] = access_token  # used dynamically in runtime
    return access_token
