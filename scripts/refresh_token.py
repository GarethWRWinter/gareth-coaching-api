# scripts/refresh_token.py

import os
import requests

def refresh_dropbox_token():
    refresh_token = os.getenv("DROPBOX_REFRESH_TOKEN")
    app_key = os.getenv("DROPBOX_APP_KEY")
    app_secret = os.getenv("DROPBOX_APP_SECRET")

    if not all([refresh_token, app_key, app_secret]):
        raise ValueError("Missing Dropbox environment variables.")

    response = requests.post(
        "https://api.dropboxapi.com/oauth2/token",
        data={
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        },
        auth=(app_key, app_secret),
    )

    if response.status_code != 200:
        raise Exception("Dropbox token refresh failed:", response.text)

    return response.json()["access_token"]
