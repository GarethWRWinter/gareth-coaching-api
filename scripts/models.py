from sqlalchemy import Column, Integer, String, Float, TIMESTAMP, JSON
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Ride(Base):
    __tablename__ = "rides"

    id = Column(Integer, primary_key=True, index=True)
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
            "id": self.id,
            "ride_id": self.ride_id,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "duration_sec": self.duration_sec,
            "distance_km": self.distance_km,
            "avg_power": self.avg_power,
            "avg_hr": self.avg_hr,
            "avg_cadence": self.avg_cadence,
            "max_power": self.max_power,
            "max_hr": self.max_hr,
            "max_cadence": self.max_cadence,
            "total_work_kj": self.total_work_kj,
            "tss": self.tss,
            "left_right_balance": self.left_right_balance,
            "power_zone_times": self.power_zone_times,
            "normalized_power": self.normalized_power,
        }
