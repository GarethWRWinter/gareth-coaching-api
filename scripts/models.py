from sqlalchemy import Column, Integer, String, Float, TIMESTAMP, JSON
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Ride(Base):
    __tablename__ = "rides"

    id = Column(Integer, primary_key=True)
    ride_id = Column(String, unique=True, index=True)
    start_time = Column(TIMESTAMP)
    duration_sec = Column(Integer)
    distance_km = Column(Float)
    avg_power = Column(Float)
    avg_hr = Column(Float)
    avg_cadence = Column(Float)
    max_power = Column(Float)
    max_hr = Column(Float)
    max_cadence = Column(Float)
    total_work_kj = Column(Float)
    tss = Column(Float)
    left_right_balance = Column(String)
    power_zone_times = Column(JSON)
    normalized_power = Column(Float)

    def to_dict(self):
        return {
            k: (v.isoformat() if hasattr(v, "isoformat") else v)
            for k, v in self.__dict__.items()
            if not k.startswith("_")
        }
