# scripts/ride_database.py

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from scripts.models import Ride  # adjust import path if needed

class RideStorageError(Exception):
    """Raised when storing or retrieving rides fails."""
    pass

# ✅ Use environment variable for DB URL
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RideStorageError("DATABASE_URL environment variable is not set")

# Create engine and session factory
engine = create_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

def store_ride(metrics: dict) -> None:
    """Insert a ride record into rides table."""
    session = SessionLocal()
    try:
        ride = Ride(**metrics)
        session.add(ride)
        session.commit()
    except Exception as exc:
        session.rollback()
        raise RideStorageError(f"Could not store ride {metrics.get('ride_id')}: {exc}") from exc
    finally:
        session.close()

def get_ride_history() -> list[dict]:
    """Fetch all ride records, newest first."""
    session = SessionLocal()
    try:
        rides = (
            session.query(Ride)
            .order_by(Ride.start_time.desc().nullslast())
            .all()
        )
        return [r.to_dict() for r in rides]
    except Exception as exc:
        raise RideStorageError(f"Failed to fetch ride history: {exc}") from exc
    finally:
        session.close()
