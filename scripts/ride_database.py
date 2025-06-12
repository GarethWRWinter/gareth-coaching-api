# scripts/ride_database.py
import os
from typing import Dict, Any, List
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from .models import Base, Ride  # models.py now has Base and Ride

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

class RideStorageError(Exception):
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
