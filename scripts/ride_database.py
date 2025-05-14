def save_ride_summary(data, summary):
    conn = sqlite3.connect("ride_data.db")
    cursor = conn.cursor()

    # 🔧 Ensure table exists
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS rides (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        distance REAL,
        avg_power REAL,
        avg_hr REAL,
        tss REAL,
        duration REAL,
        zones TEXT
    )
    """)

    # ✅ Insert summary
    cursor.execute("""
    INSERT INTO rides (timestamp, distance, avg_power, avg_hr, tss, duration, zones)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        summary["timestamp"],
        summary["distance_km"],
        summary["avg_power"],
        summary["avg_heart_rate"],
        summary["tss"],
        summary["duration_minutes"],
        json.dumps(summary["time_in_zones"])
    ))

    conn.commit()
    conn.close()
