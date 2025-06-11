# scripts/ride_database.py

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import Column, Integer, String, Float, JSON, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import os

# --- Setup SQLAlchemy engine and session ---
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost/dbname")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

Base = declarative_base()

class Ride(Base):
    __tablename__ = "rides"
    id = Column(Integer, primary_key=True, index=True)
    ride_id = Column(String, unique=True, index=True, nullable=False)
    start_time = Column(DateTime)
    duration_sec = Column(Integer, nullable=False)
    distance_km = Column(Float)
    avg_power = Column(Float)
    max_power = Column(Float)
    avg_hr = Column(Float)
    max_hr = Column(Float)
    avg_cadence = Column(Float)
    max_cadence = Column(Float)
    total_work_kj = Column(Float, nullable=False)
    normalized_power = Column(Float)
    tss = Column(Float)
    left_right_balance = Column(Float)
    power_zone_times = Column(JSON)

def init_db():
    """Create tables if they don't exist."""
    Base.metadata.create_all(bind=engine)

def get_ride_history():
    """Fetch all rides ordered by start_time descending."""
    session = SessionLocal()
    try:
        rides = session.query(Ride).order_by(Ride.start_time.desc().nullslast()).all()
        return [r.__dict__ for r in rides]
    finally:
        session.close()

def store_ride(metrics: dict):
    """
    Insert or update a ride.
    Uses PostgreSQL ON CONFLICT to upsert by ride_id.
    """
    session = SessionLocal()
    stmt = insert(Ride).values(**metrics)
    do_update_cols = {
        col.name: getattr(stmt.excluded, col.name)
        for col in Ride.__table__.columns
        if col.name != "id"  # Skip the auto-generated primary key
    }
    stmt = stmt.on_conflict_do_update(
        index_elements=["ride_id"],
        set_=do_update_cols
    )
    session.execute(stmt)
    session.commit()
    session.close()
