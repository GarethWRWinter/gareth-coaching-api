from sqlalchemy import create_engine, text

def add_hr_zone_times_column():
    engine = create_engine("sqlite:///ride_data.db")
    with engine.connect() as conn:
        conn.execute(text("ALTER TABLE rides ADD COLUMN hr_zone_times JSON"))
    print("✅ hr_zone_times column added to rides table.")

if __name__ == "__main__":
    add_hr_zone_times_column()
