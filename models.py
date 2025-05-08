from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Float, DateTime, String

Base = declarative_base()

class RideData(Base):
    __tablename__ = "ride_data"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, index=True)
    power = Column(Float)
    heart_rate = Column(Float)
    cadence = Column(Float)
    speed = Column(Float)
    distance = Column(Float)
    temperature = Column(Float)
    filename = Column(String)

class TimeInZone(Base):
    __tablename__ = "time_in_zone"

    id = Column(Integer, primary_key=True, index=True)
    zone = Column(String)
    seconds = Column(Integer)
    filename = Column(String)

class HRTimeInZone(Base):
    __tablename__ = "hr_time_in_zone"

    id = Column(Integer, primary_key=True, index=True)
    zone = Column(String)
    seconds = Column(Integer)
    filename = Column(String)

class FTPRecord(Base):
    __tablename__ = "ftp_records"

    id = Column(Integer, primary_key=True, index=True)
    ftp = Column(Float)
    date_set = Column(DateTime)
    source = Column(String)
