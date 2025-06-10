from sqlalchemy import create_engine, text

def create_rides_table():
    engine = create_engine("sqlite:///ride_data.db")
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
                power_zone_times JSON,
                hr_zone_times JSON
            );
        """))
    print("✅ rides table created successfully.")

if __name__ == "__main__":
    create_rides_table()
