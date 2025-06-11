# scripts/ride_database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from scripts.models import Ride  # adjust import path as needed

# Define this exception for error handling
class RideStorageError(Exception):
    """Raised when storing a ride to the database fails."""
    pass

# Set up database
DATABASE_URL = "..."  # your Render DB URL or env var
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)

def store_ride(metrics: dict) -> None:
    """Store a processed ride metrics dict into the database."""
    session = SessionLocal()
    try:
        ride = Ride(**metrics)
        session.add(ride)
        session.commit()
    except Exception as exc:
        session.rollback()
        raise RideStorageError(
            f"Could not store ride {metrics.get('ride_id')}: {exc}"
        ) from exc
    finally:
        session.close()

def get_ride_history() -> list[dict]:
    """Retrieve all stored rides, ordered newest first."""
    session = SessionLocal()
    try:
        rides = (
            session.query(Ride)
            .order_by(Ride.start_time.desc().nullslast())
            .all()
        )
        return [r.to_dict() for r in rides]  # ensure Ride model has .to_dict()
    except Exception as exc:
        raise RideStorageError(f"Failed fetching ride history: {exc}") from exc
    finally:
        session.close()
