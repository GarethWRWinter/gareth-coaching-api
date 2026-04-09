"""
Recalculate CTL/ATL/TSB (Performance Management Chart) from all ride TSS data.

Usage: .venv/bin/python scripts/recalc_pmc.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models.ride import Ride
from app.models.user import User
from app.services.metrics_service import recalculate_from_date

USER_EMAIL = "gareth@test.com"


def main():
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == USER_EMAIL).first()
        if not user:
            print(f"User {USER_EMAIL} not found!")
            return

        print(f"User: {user.email} (FTP: {user.ftp})")

        # Find earliest ride with TSS
        earliest_ride = (
            db.query(Ride)
            .filter(Ride.user_id == user.id, Ride.tss.isnot(None))
            .order_by(Ride.ride_date.asc())
            .first()
        )

        if not earliest_ride:
            print("No rides with TSS found!")
            return

        start = earliest_ride.ride_date.date()
        print(f"Earliest ride: {start}")

        # Count rides with TSS
        ride_count = (
            db.query(Ride)
            .filter(Ride.user_id == user.id, Ride.tss.isnot(None))
            .count()
        )
        print(f"Rides with TSS data: {ride_count}")

        print(f"\nRecalculating PMC from {start}...")
        recalculate_from_date(db, user.id, start)

        # Show current fitness state
        from app.models.metrics import DailyMetrics
        latest = (
            db.query(DailyMetrics)
            .filter(DailyMetrics.user_id == user.id)
            .order_by(DailyMetrics.date.desc())
            .first()
        )

        if latest:
            print(f"\n✓ PMC recalculation complete!")
            print(f"  Date:      {latest.date}")
            print(f"  CTL:       {latest.ctl:.1f}")
            print(f"  ATL:       {latest.atl:.1f}")
            print(f"  TSB:       {latest.tsb:.1f}")
            print(f"  Ramp Rate: {latest.ramp_rate:.1f}")

        # Count total daily metrics rows
        total_metrics = (
            db.query(DailyMetrics)
            .filter(DailyMetrics.user_id == user.id)
            .count()
        )
        print(f"\n  Total daily metrics rows: {total_metrics}")

    finally:
        db.close()


if __name__ == "__main__":
    main()
