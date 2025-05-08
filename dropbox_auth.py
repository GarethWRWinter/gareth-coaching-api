import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()  # optional, in case you're running locally and have a .env file

def refresh_dropbox_access_token():
    print("🔁 Refreshing Dropbox access token...")

    refresh_token = os.getenv("DROPBOX_REFRESH_TOKEN")
    client_id = os.getenv("DROPBOX_APP_KEY")
    client_secret = os.getenv("DROPBOX_APP_SECRET")

    if not refresh_token or not client_id or not client_secret:
        raise ValueError("❌ Missing Dropbox credentials in environment variables.")

    response = requests.post(
        "https://api.dropbox.com/oauth2/token",
        auth=(client_id, client_secret),
        data={
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        },
    )

    if response.status_code != 200:
        raise Exception(f"❌ Failed to refresh access token: {response.text}")

    access_token = response.json().get("access_token")

    if not access_token:
        raise Exception("❌ No access token received from Dropbox.")

    # Save access token to environment (for local use)
    os.environ["DROPBOX_TOKEN"] = access_token

    print("✅ Dropbox access token refreshed successfully.")
    return access_token
