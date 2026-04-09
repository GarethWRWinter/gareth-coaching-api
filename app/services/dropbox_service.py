"""
Dropbox OAuth 2.0 integration and FIT file sync.

Flow:
1. User clicks "Connect Dropbox" -> redirected to Dropbox auth page
2. User authorizes -> Dropbox redirects back with auth code
3. We exchange code for access/refresh tokens
4. User configures folder path (default: /cycling)
5. On sync, we scan the folder for .fit files and import them as rides
"""

import json
import logging
from datetime import datetime, timedelta, timezone

import httpx
from sqlalchemy.orm import Session

from app.config import settings
from app.models.integration import DropboxToken
from app.models.ride import Ride, RideData
from app.models.user import User
from app.services.dedup_service import find_strava_duplicate, merge_strava_into_dropbox
from app.services.ride_service import create_ride_from_fit

logger = logging.getLogger(__name__)

AUTH_URL = "https://www.dropbox.com/oauth2/authorize"
TOKEN_URL = "https://api.dropboxapi.com/oauth2/token"
LIST_FOLDER_URL = "https://api.dropboxapi.com/2/files/list_folder"
DOWNLOAD_URL = "https://content.dropboxapi.com/2/files/download"


def get_auth_url(user_id: str) -> str:
    """Generate Dropbox OAuth authorization URL."""
    params = {
        "client_id": settings.dropbox_client_id,
        "response_type": "code",
        "token_access_type": "offline",
        "redirect_uri": settings.dropbox_redirect_uri,
        "state": user_id,
    }
    query = "&".join(f"{k}={v}" for k, v in params.items())
    return f"{AUTH_URL}?{query}"


async def exchange_code(db: Session, user_id: str, code: str) -> DropboxToken:
    """Exchange authorization code for access/refresh tokens."""
    async with httpx.AsyncClient() as client:
        response = await client.post(TOKEN_URL, data={
            "client_id": settings.dropbox_client_id,
            "client_secret": settings.dropbox_client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": settings.dropbox_redirect_uri,
        })
        response.raise_for_status()
        data = response.json()

    access_token = data["access_token"]
    refresh_token = data["refresh_token"]
    expires_in = data.get("expires_in", 14400)
    account_id = data.get("account_id")
    expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)

    # Upsert: delete existing, create new
    db.query(DropboxToken).filter(DropboxToken.user_id == user_id).delete()

    token = DropboxToken(
        user_id=user_id,
        access_token=access_token,
        refresh_token=refresh_token,
        expires_at=expires_at,
        account_id=account_id,
    )
    db.add(token)
    db.commit()
    db.refresh(token)
    return token


async def _refresh_token_if_needed(db: Session, token: DropboxToken) -> DropboxToken:
    """Refresh access token if expired. Returns the token with a valid access_token."""
    expires_at = token.expires_at
    # Make timezone-aware if naive
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at > datetime.now(timezone.utc):
        return token

    if not token.refresh_token:
        raise ValueError(
            "Dropbox access token has expired and no refresh token is available. "
            "Please disconnect and re-authorize Dropbox."
        )

    async with httpx.AsyncClient() as client:
        response = await client.post(TOKEN_URL, data={
            "grant_type": "refresh_token",
            "refresh_token": token.refresh_token,
            "client_id": settings.dropbox_client_id,
            "client_secret": settings.dropbox_client_secret,
        })
        response.raise_for_status()
        data = response.json()

    token.access_token = data["access_token"]
    expires_in = data.get("expires_in", 14400)
    token.expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
    db.commit()

    return token


async def sync_fit_files(db: Session, user_id: str, limit: int = 10) -> list[dict]:
    """
    Scan the configured Dropbox folder for FIT files and import them as rides.
    Skips files that have already been imported (by matching source filename).
    Imports newest files first, up to `limit` new files per sync.

    Returns a list of dicts for each successfully synced ride:
        [{"title": ..., "id": ..., "date": ...}]
    """
    token = db.query(DropboxToken).filter(DropboxToken.user_id == user_id).first()
    if not token:
        raise ValueError("Dropbox not connected")

    token = await _refresh_token_if_needed(db, token)

    # Fetch the user object (needed by create_ride_from_fit)
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise ValueError("User not found")

    # Get existing filenames to skip duplicates (fit_file_path stores original filename)
    existing_rides = db.query(Ride.fit_file_path).filter(
        Ride.user_id == user_id,
        Ride.source == "dropbox",
        Ride.fit_file_path.isnot(None),
    ).all()
    existing_filenames = {r.fit_file_path for r in existing_rides}

    # List files in the configured folder (handle pagination)
    headers = {"Authorization": f"Bearer {token.access_token}"}
    all_entries = []

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            LIST_FOLDER_URL,
            headers={**headers, "Content-Type": "application/json"},
            json={"path": token.folder_path, "recursive": False, "limit": 2000},
        )
        response.raise_for_status()
        folder_data = response.json()
        all_entries.extend(folder_data.get("entries", []))

        # Handle pagination
        while folder_data.get("has_more"):
            cursor = folder_data["cursor"]
            response = await client.post(
                "https://api.dropboxapi.com/2/files/list_folder/continue",
                headers={**headers, "Content-Type": "application/json"},
                json={"cursor": cursor},
            )
            response.raise_for_status()
            folder_data = response.json()
            all_entries.extend(folder_data.get("entries", []))

    # Filter for FIT files only
    fit_files = [
        entry for entry in all_entries
        if entry.get(".tag") == "file"
        and (entry["name"].endswith(".fit") or entry["name"].endswith(".FIT"))
    ]

    # Sort by name (descending = newest first for date-prefixed Wahoo files)
    fit_files.sort(key=lambda e: e["name"], reverse=True)

    # Skip already imported files
    new_files = [f for f in fit_files if f["name"] not in existing_filenames]
    files_to_sync = new_files[:limit]

    logger.info(
        "Dropbox sync: %d total FIT files, %d already imported, syncing %d new",
        len(fit_files), len(existing_filenames), len(files_to_sync),
    )

    synced_rides = []

    for fit_entry in files_to_sync:
        file_path = fit_entry["path_lower"]
        filename = fit_entry["name"]

        try:
            # Download FIT file content
            async with httpx.AsyncClient(timeout=30.0) as client:
                download_response = await client.post(
                    DOWNLOAD_URL,
                    headers={
                        "Authorization": f"Bearer {token.access_token}",
                        "Dropbox-API-Arg": json.dumps({"path": file_path}),
                    },
                )
                download_response.raise_for_status()
                fit_content = download_response.content

            # Create ride from FIT data (set source to "dropbox" for dedup)
            ride = create_ride_from_fit(db, user, fit_content, filename, source="dropbox")

            # Check for existing Dropbox ride with same date+duration (prevent self-dupes)
            existing_dbx = (
                db.query(Ride)
                .filter(
                    Ride.user_id == user_id,
                    Ride.source == "dropbox",
                    Ride.id != ride.id,
                    Ride.ride_date == ride.ride_date,
                    Ride.duration_seconds == ride.duration_seconds,
                )
                .first()
            )
            if existing_dbx:
                # Already have this ride — remove the duplicate we just created
                db.query(RideData).filter(RideData.ride_id == ride.id).delete()
                db.delete(ride)
                db.commit()
                logger.info("Skipped duplicate Dropbox FIT: %s (matches ride %s)", filename, existing_dbx.id)
                continue

            # If a Strava ride already exists for the same activity, merge it
            strava_dup = find_strava_duplicate(
                db, user_id, ride.ride_date, ride.duration_seconds,
            )
            if strava_dup:
                merge_strava_into_dropbox(db, ride, strava_dup)
                db.commit()

            synced_rides.append({
                "title": ride.title,
                "id": ride.id,
                "date": str(ride.ride_date),
            })
            logger.info("Synced FIT file from Dropbox: %s", filename)

        except Exception:
            logger.exception("Failed to sync FIT file from Dropbox: %s", filename)
            db.rollback()  # Reset session state so next file can proceed
            continue

    # Update last sync timestamp
    token.last_sync_at = datetime.now(timezone.utc)
    db.commit()

    return synced_rides


def get_connection_status(db: Session, user_id: str) -> dict:
    """Check if Dropbox is connected and return status info."""
    token = db.query(DropboxToken).filter(DropboxToken.user_id == user_id).first()
    if not token:
        return {
            "connected": False,
            "account_id": None,
            "folder_path": None,
            "last_sync_at": None,
        }

    return {
        "connected": True,
        "account_id": token.account_id,
        "folder_path": token.folder_path,
        "last_sync_at": str(token.last_sync_at) if token.last_sync_at else None,
    }


def disconnect(db: Session, user_id: str) -> None:
    """Remove Dropbox connection."""
    db.query(DropboxToken).filter(DropboxToken.user_id == user_id).delete()
    db.commit()
