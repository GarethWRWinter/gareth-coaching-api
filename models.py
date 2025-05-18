from pydantic import BaseModel
from sqlalchemy import Column, Integer, Float, String
from sqlalchemy.ext.declarative import declarative_base

# This tells SQLAlchemy how to build the table
Base = declarative_base()

# This is your ride data table
class RideData(Base):
    __tablename__ = "ride_data"

    id = Column(Integer, primary_key=True, index=True)
    ride_id = Column(String, index=True)
    timestamp = Column(String)
    power = Column(Integer)
    heart_rate = Column(Integer)
    cadence = Column(Integer)
    speed = Column(Float)
    distance = Column(Float)
    left_right_balance = Column(Integer)
    torque = Column(Float)  # <--- You asked to include torque here

# This is the Pydantic model used for validation and API responses
class RideDataSchema(BaseModel):
    ride_id: str
    timestamp: str
    power: int | None = None
    heart_rate: int | None = None
    cadence: int | None = None
    speed: float | None = None
    distance: float | None = None
    left_right_balance: int | None = None
    torque: float | None = None

    class Config:
        orm_mode = True
