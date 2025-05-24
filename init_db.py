from models import Base
from sqlalchemy import create_engine

engine = create_engine("sqlite:///ride_data.db")
Base.metadata.create_all(engine)

print("✅ Database initialized: ride_data.db")
