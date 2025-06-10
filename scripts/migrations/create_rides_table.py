# scripts/migrations/create_rides_table.py

from sqlalchemy import create_engine, text

DATABASE_URL = "sqlite:///ride_data.db"

def create_rides_table():
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS rides (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ride_id TEXT UNIQUE,
                start_time DATETIME,
                duration_sec INTEGER,
                distance_km FLOAT,
                avg_power FLOAT,
                avg_hr FLOAT,
                avg_cadence FLOAT,
                max_power FLOAT,
                max_hr FLOAT,
                max_cadence FLOAT,
                total_work_kj FLOAT,
                tss FLOAT,
                normalized_power FLOAT,
                left_right_balance TEXT,
                power_zone_times JSON
            );
        """))
        print("✅ rides table created successfully.")

if __name__ == "__main__":
    create_rides_table()
