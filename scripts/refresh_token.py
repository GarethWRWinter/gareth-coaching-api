import os
import requests
from dotenv import load_dotenv

load_dotenv()  # Optional: loads from .env file

APP_KEY = "3ge3h3mssudmqzk"
APP_SECRET = "u0bt5xb35zcsrfz"
REFRESH_TOKEN = "SVwgdziU4HAAAAAAAAAAASSBx0chH1-qP7vM0IcYLXecS_2Ttj1n2DSfdhDhOU32"

def get_new_access_token():
    response = requests.post(
        "https://api.dropboxapi.com/oauth2/token",
        auth=(APP_KEY, APP_SECRET),
        data={
            "grant_type": "refresh_token",
            "refresh_token": REFRESH_TOKEN
        }
    )

    if response.status_code == 200:
        token = response.json()["access_token"]
        print("✅ New access token:\n")
        print(token)
        return token
    else:
        print("❌ Failed to refresh token")
        print(response.text)
        return None

if __name__ == "__main__":
    get_new_access_token()
