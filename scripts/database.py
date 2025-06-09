from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://gareth_coaching_api_db_user:68HF33JZZ1lvKk9UMsZrOLXPlsuulYUC@dpg-d0ts7qre5dus73885pi0-a.oregon-postgres.render.com/gareth_coaching_api_db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
