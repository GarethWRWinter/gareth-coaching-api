# scripts/models.py
from sqlalchemy import Column, Integer, Float, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Ride(Base):
    __tablename__ = "rides"

    id = Column(Integer, primary_key=True)
    filename = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    duration_seconds = Column(Integer)
    avg_power = Column(Float)
    avg_heart_rate = Column(Float)
    max_power = Column(Float)
    max_heart_rate = Column(Float)
    tss = Column(Float)
