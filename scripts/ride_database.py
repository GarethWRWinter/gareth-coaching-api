def store_ride(summary: dict, full_data: list):
    try:
        initialize_database()
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO rides (
                ride_id, date, duration_min, avg_power, avg_heart_rate, tss, full_data
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            summary["ride_id"],
            summary["start_time"].split(" ")[0],
            summary["duration_min"],
            summary["avg_power"],
            summary["avg_heart_rate"],
            summary["tss"],
            json.dumps(full_data, default=default_json)
        ))

        conn.commit()
        conn.close()
        logger.info(f"Stored ride {summary['ride_id']} to DB")

    except Exception as e:
        logger.exception("Failed to store ride in database")
        raise
