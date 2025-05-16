import sqlite3

DB_PATH = "ride_data.db"

def init_db():
    print("🔧 Initializing database...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 🚧 COMMENT THIS IN PROD AFTER TESTING
    # cursor.execute("DROP TABLE IF EXISTS rides")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rides (
            ride_id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            duration INTEGER,
            avg_power REAL,
            avg_hr REAL,
            avg_cadence REAL,
            distance REAL,
            tss REAL,
            zone_durations TEXT,
            pedal_balance REAL,
            normalized_power REAL,
            variability_index REAL
        )
    """)
    conn.commit()
    conn.close()
    print("✅ rides table created or confirmed")

def save_ride_summary(summary):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO rides (
            timestamp, duration, avg_power, avg_hr, avg_cadence, distance, tss,
            zone_durations, pedal_balance, normalized_power, variability_index
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        summary.get("timestamp"),
        summary.get("duration"),
        summary.get("avg_power"),
        summary.get("avg_hr"),
        summary.get("avg_cadence"),
        summary.get("distance"),
        summary.get("training_stress_score"),
        str(summary.get("time_in_zones")),
        summary.get("pedal_balance"),
        summary.get("normalized_power"),
        summary.get("variability_index")
    ))
    conn.commit()
    conn.close()

def get_all_rides():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT ride_id, timestamp, duration, avg_power, tss FROM rides ORDER BY timestamp DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_ride_by_id(ride_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM rides WHERE ride_id = ?", (ride_id,))
    row = cursor.fetchone()
    conn.close()
    return row
