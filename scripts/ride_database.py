def store_ride(ride_data: dict):
    """
    Stores a new ride record in the database, ignoring if the ride_id already exists.
    Uses Postgres ON CONFLICT DO NOTHING to avoid duplicate key errors.
    Ensures all bind parameters have a value (None if missing).
    """
    db: Session = SessionLocal()

    # Ensure all expected keys are present
    required_keys = [
        "ride_id", "start_time", "duration_sec", "distance_km",
        "avg_power", "avg_hr", "avg_cadence", "max_power", "max_hr", "max_cadence",
        "total_work_kj", "tss", "normalized_power", "left_right_balance", "power_zone_times"
    ]
    for key in required_keys:
        if key not in ride_data:
            ride_data[key] = None

    insert_query = text("""
        INSERT INTO rides (
            ride_id, start_time, duration_sec, distance_km,
            avg_power, avg_hr, avg_cadence, max_power, max_hr, max_cadence,
            total_work_kj, tss, normalized_power, left_right_balance, power_zone_times
        ) VALUES (
            :ride_id, :start_time, :duration_sec, :distance_km,
            :avg_power, :avg_hr, :avg_cadence, :max_power, :max_hr, :max_cadence,
            :total_work_kj, :tss, :normalized_power, :left_right_balance, :power_zone_times
        )
        ON CONFLICT (ride_id) DO NOTHING;
    """)
    db.execute(insert_query, ride_data)
    db.commit()
    db.close()
