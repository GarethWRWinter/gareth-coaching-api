import os
import requests

def refresh_access_token() -> str:
    refresh_token = os.environ.get("DROPBOX_REFRESH_TOKEN")
    app_key = os.environ.get("DROPBOX_APP_KEY")
    app_secret = os.environ.get("DROPBOX_APP_SECRET")

    response = requests.post(
        "https://api.dropbox.com/oauth2/token",
        auth=(app_key, app_secret),
        data={
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
        }
    )

    response.raise_for_status()
    access_token = response.json()["access_token"]
    return access_token
