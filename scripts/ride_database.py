import sqlite3
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Adjust this connection string as needed
DATABASE_URL = "sqlite:///ride_data.db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


def get_ftp() -> float:
    """
    Fetch the current FTP value from the athletes table.
    If not found, return a default value.
    """
    with engine.connect() as conn:
        result = conn.execute(text("SELECT ftp FROM athletes LIMIT 1"))
        row = result.fetchone()
        return row[0] if row and row[0] else 308.0  # default FTP if not set


def update_ftp(new_ftp: float):
    """
    Update FTP in the athletes table.
    """
    with engine.connect() as conn:
        conn.execute(text("UPDATE athletes SET ftp = :ftp"), {"ftp": new_ftp})
        conn.commit()
