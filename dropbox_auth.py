import os
import requests

def refresh_dropbox_token():
    print("Refreshing Dropbox token...")
    url = "https://api.dropbox.com/oauth2/token"
    data = {
        "grant_type": "refresh_token",
        "refresh_token": os.environ["DROPBOX_REFRESH_TOKEN"],
        "client_id": os.environ["DROPBOX_APP_KEY"],
        "client_secret": os.environ["DROPBOX_APP_SECRET"],
    }

    response = requests.post(url, data=data)
    response.raise_for_status()

    new_token = response.json()["access_token"]
    os.environ["DROPBOX_TOKEN"] = new_token
    return new_token
