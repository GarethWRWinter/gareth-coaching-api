"""
Delete all rides for gareth@test.com, then trigger a Dropbox re-sync
with corrected metrics (device NP/TSS/IF/FTP) and classified ride names.

Usage: .venv/bin/python scripts/cleanup_and_reimport.py
"""

import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models.ride import Ride, RideData
from app.models.user import User
from app.services.dropbox_service import sync_fit_files

USER_EMAIL = "gareth@test.com"
BATCH_SIZE = 50  # Import 50 files per batch


def delete_all_rides(db, user_id: str) -> int:
    """Delete all rides and ride_data for a user."""
    # Count first
    ride_count = db.query(Ride).filter(Ride.user_id == user_id).count()
    if ride_count == 0:
        print("No rides to delete.")
        return 0

    print(f"Deleting {ride_count} rides and all associated ride_data...")

    # Delete ride_data first (FK constraint)
    ride_ids = [r.id for r in db.query(Ride.id).filter(Ride.user_id == user_id).all()]

    # Batch delete ride_data for performance
    batch = 100
    for i in range(0, len(ride_ids), batch):
        chunk = ride_ids[i:i + batch]
        deleted = db.query(RideData).filter(RideData.ride_id.in_(chunk)).delete(synchronize_session=False)
        if (i // batch) % 5 == 0:
            print(f"  Deleted ride_data batch {i // batch + 1}... ({i + len(chunk)}/{len(ride_ids)} rides processed)")

    # Delete rides
    db.query(Ride).filter(Ride.user_id == user_id).delete(synchronize_session=False)
    db.commit()

    print(f"✓ Deleted {ride_count} rides and all their data points.")
    return ride_count


async def reimport_from_dropbox(db, user_id: str):
    """Re-sync all FIT files from Dropbox in batches."""
    total_synced = 0
    batch_num = 0

    while True:
        batch_num += 1
        print(f"\nBatch {batch_num}: Syncing up to {BATCH_SIZE} files...")

        rides = await sync_fit_files(db, user_id, limit=BATCH_SIZE)
        synced = len(rides)
        total_synced += synced

        if synced > 0:
            print(f"  ✓ Synced {synced} rides (total: {total_synced})")
            # Print a few example titles
            for r in rides[:3]:
                print(f"    - {r['title']} ({r['date'][:10]})")
            if synced > 3:
                print(f"    ... and {synced - 3} more")
        else:
            print("  No more files to sync.")
            break

    print(f"\n✓ Re-import complete: {total_synced} rides synced with corrected metrics.")
    return total_synced


async def main():
    db = SessionLocal()
    try:
        # Find user
        user = db.query(User).filter(User.email == USER_EMAIL).first()
        if not user:
            print(f"User {USER_EMAIL} not found!")
            return

        print(f"User: {user.email} (ID: {user.id}, FTP: {user.ftp})")
        print("=" * 60)

        # Step 1: Delete all existing rides
        print("\n--- Step 1: Delete all existing rides ---")
        delete_all_rides(db, user.id)

        # Step 2: Re-import from Dropbox with corrected code
        print("\n--- Step 2: Re-import from Dropbox ---")
        await reimport_from_dropbox(db, user.id)

        # Step 3: Verify
        print("\n--- Step 3: Verify ---")
        ride_count = db.query(Ride).filter(Ride.user_id == user.id).count()
        data_count = db.query(RideData).join(Ride).filter(Ride.user_id == user.id).count()

        # Sample a few rides
        sample_rides = (
            db.query(Ride)
            .filter(Ride.user_id == user.id)
            .order_by(Ride.ride_date.desc())
            .limit(10)
            .all()
        )

        print(f"\nTotal rides: {ride_count}")
        print(f"Total data points: {data_count:,}")
        print(f"User FTP (updated): {user.ftp}")
        print("\nRecent rides:")
        for r in sample_rides:
            date_str = r.ride_date.strftime("%Y-%m-%d") if r.ride_date else "?"
            print(
                f"  {date_str} | {r.title:<30} | "
                f"NP={r.normalized_power or 0:.0f}w  "
                f"TSS={r.tss or 0:.0f}  "
                f"IF={r.intensity_factor or 0:.2f}  "
                f"FTP@{r.ftp_at_time or 0}w"
            )

    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(main())
