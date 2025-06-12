# scripts/ride_database.py

import os
from typing import Any
from sqlalchemy import create_engine, Column, Integer, Float, String, JSON, select
from sqlalchemy.orm import declarative_base, Session

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost/db")

Base = declarative_base()
engine = create_engine(DATABASE_URL, echo=False, future=True)


class Ride(Base):
    __tablename__ = "rides"

    id = Column(Integer, primary_key=True)
    ride_id = Column(String, unique=True, nullable=False)
    avg_power = Column(Float, nullable=False)
    duration_sec = Column(Integer, nullable=False)
    ftp_used = Column(Integer, nullable=False)
    extra = Column(JSON, nullable=True)


class RideDBError(Exception):
    pass


def init_db():
    Base.metadata.create_all(bind=engine)


def store_ride(data: dict[str, Any]):
    ride = Ride(
        ride_id=data["ride_id"],
        avg_power=data["avg_power"],
        duration_sec=data["duration_sec"],
        ftp_used=data["ftp_used"],
        extra={k: data[k] for k in data if k not in ("ride_id", "avg_power", "duration_sec", "ftp_used")},
    )
    try:
        with Session(engine) as session:
            session.add(ride)
            session.commit()
    except Exception as e:
        raise RideDBError(e)


def get_ride_history() -> list[dict]:
    with Session(engine) as session:
        stmt = select(Ride)
        rides = session.scalars(stmt).all()
        return [
            {
                "ride_id": r.ride_id,
                "avg_power": r.avg_power,
                "duration_sec": r.duration_sec,
                "ftp_used": r.ftp_used,
                **(r.extra or {}),
            }
            for r in rides
        ]
