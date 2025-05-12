import sqlite3

def fetch_ride_history(limit=7):
    conn = sqlite3.connect("ride_data.db")
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT
            filename, timestamp, duration_s,
            avg_power, max_power,
            avg_heart_rate, max_heart_rate,
            tss, zone1_min, zone2_min, zone3_min,
            zone4_min, zone5_min, zone6_min
        FROM rides
        ORDER BY timestamp DESC
        LIMIT ?
        """,
        (limit,)
    )

    rows = cursor.fetchall()
    conn.close()

    ride_keys = [
        "filename", "timestamp", "duration_s",
        "avg_power", "max_power",
        "avg_heart_rate", "max_heart_rate",
        "tss", "zone1_min", "zone2_min", "zone3_min",
        "zone4_min", "zone5_min", "zone6_min"
    ]

    return [dict(zip(ride_keys, row)) for row in rows]
