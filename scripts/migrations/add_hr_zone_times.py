# scripts/migrations/add_hr_zone_times.py

from sqlalchemy import create_engine, text

# Path to your SQLite DB
DATABASE_URL = "sqlite:///ride_data.db"

def add_hr_zone_times_column():
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        conn.execute(text("""
            ALTER TABLE rides ADD COLUMN hr_zone_times JSON;
        """))
        print("✅ hr_zone_times column added to rides table.")

if __name__ == "__main__":
    add_hr_zone_times_column()
