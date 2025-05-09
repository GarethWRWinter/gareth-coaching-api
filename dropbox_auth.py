import os
import requests

def get_dropbox_access_token():
    refresh_token = os.getenv("DROPBOX_REFRESH_TOKEN")
    app_key = os.getenv("DROPBOX_APP_KEY")
    app_secret = os.getenv("DROPBOX_APP_SECRET")

    if not refresh_token or not app_key or not app_secret:
        raise Exception("Missing Dropbox environment variables")

    print("Refreshing Dropbox token...")

    response = requests.post(
        "https://api.dropbox.com/oauth2/token",
        auth=(app_key, app_secret),
        data={"grant_type": "refresh_token", "refresh_token": refresh_token},
    )

    if response.status_code != 200:
        raise Exception(f"Failed to refresh token: {response.text}")

    access_token = response.json()["access_token"]
    return access_token
