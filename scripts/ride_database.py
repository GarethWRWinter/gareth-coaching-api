from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://...your full URL..."
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Ride(Base):
    __tablename__ = 'rides'

    id = Column(Integer, primary_key=True, index=True)
    ride_id = Column(String, unique=True, nullable=False)
    start_time = Column(DateTime)
    duration_sec = Column(Integer)
    distance_km = Column(Float)
    avg_power = Column(Float)
    max_power = Column(Float)
    avg_hr = Column(Float)
    max_hr = Column(Float)
    avg_cadence = Column(Float)
    max_cadence = Column(Float)
    total_work_kj = Column(Float)
    tss = Column(Float)
    left_right_balance = Column(String)
    power_zone_times = Column(JSON)
    normalized_power = Column(Float)

    def to_dict(self):
        return {
            c.name: getattr(self, c.name)
            for c in self.__table__.columns
        }

class RideStorageError(Exception):
    pass

def store_ride(data: dict):
    session = SessionLocal()
    try:
        ride = Ride(**data)
        session.add(ride)
        session.commit()
    except Exception as e:
        session.rollback()
        raise RideStorageError(str(e))
    finally:
        session.close()

def get_ride_history():
    session = SessionLocal()
    try:
        rides = session.query(Ride).order_by(Ride.start_time.desc()).all()
        return [r.to_dict() for r in rides]
    finally:
        session.close()
