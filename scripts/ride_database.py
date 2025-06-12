# scripts/ride_database.py

from typing import Dict, Any, List
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import SQLAlchemyError
from .models import Ride  # contains Ride model with Base metadata

DATABASE_URL = os.getenv("DATABASE_URL")  # should be full Postgres URL

# SQLAlchemy Base
Base = declarative_base()

# Create engine
engine = create_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

class RideStorageError(Exception):
    """Raised when storing or fetching rides fails."""
    pass

def store_ride(data: Dict[str, Any]) -> None:
    session = SessionLocal()
    try:
        ride = Ride(**data)
        session.add(ride)
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        raise RideStorageError(f"Error storing ride: {e}")
    finally:
        session.close()

def get_ride_history() -> List[Dict[str, Any]]:
    session = SessionLocal()
    try:
        rides = session.query(Ride).all()
        return [r.to_dict() for r in rides]
    except SQLAlchemyError as e:
        raise RideStorageError(f"Failed to fetch ride history: {e}")
    finally:
        session.close()
