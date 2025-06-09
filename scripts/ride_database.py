from sqlalchemy import text

def store_ride(ride_data: dict):
    """
    Stores a new ride record in the database, ignoring if the ride_id already exists.
    """
    db: Session = SessionLocal()
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
