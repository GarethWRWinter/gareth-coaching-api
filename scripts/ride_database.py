import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '../ride_data.db')

def init_db():
    print("🔧 Initializing database...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS rides (
            ride_id TEXT PRIMARY KEY,
            timestamp TEXT,
            duration INTEGER,
            avg_power INTEGER,
            avg_heart_rate INTEGER,
            avg_cadence INTEGER,
            max_power INTEGER,
            max_heart_rate INTEGER,
            max_cadence INTEGER,
            distance REAL,
            energy_output REAL,
            training_stress_score REAL,
            time_in_zone_1 INTEGER,
            time_in_zone_2 INTEGER,
            time_in_zone_3 INTEGER,
            time_in_zone_4 INTEGER,
            time_in_zone_5 INTEGER,
            time_in_zone_6 INTEGER,
            pedal_balance REAL
        )
    ''')
    conn.commit()
    conn.close()
    print("✅ rides table created or confirmed")

def save_ride_summary(summary):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO rides (
            ride_id, timestamp, duration, avg_power, avg_heart_rate,
            avg_cadence, max_power, max_heart_rate, max_cadence,
            distance, energy_output, training_stress_score,
            time_in_zone_1, time_in_zone_2, time_in_zone_3,
            time_in_zone_4, time_in_zone_5, time_in_zone_6,
            pedal_balance
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        summary["ride_id"],
        summary["timestamp"],
        summary["duration"],
        summary["avg_power"],
        summary["avg_heart_rate"],
        summary["avg_cadence"],
        summary["max_power"],
        summary["max_heart_rate"],
        summary["max_cadence"],
        summary["distance"],
        summary["energy_output"],
        summary["training_stress_score"],
        summary["time_in_zones"]["Z1"],
        summary["time_in_zones"]["Z2"],
        summary["time_in_zones"]["Z3"],
        summary["time_in_zones"]["Z4"],
        summary["time_in_zones"]["Z5"],
        summary["time_in_zones"]["Z6"],
        summary["pedal_balance"]
    ))
    conn.commit()
    conn.close()

def get_all_rides():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT ride_id, timestamp, duration, avg_power, training_stress_score
        FROM rides ORDER BY timestamp DESC
    ''')
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            "ride_id": row[0],
            "timestamp": row[1],
            "duration": row[2],
            "avg_power": row[3],
            "training_stress_score": row[4],
        }
        for row in rows
    ]

def get_ride_by_id(ride_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM rides WHERE ride_id = ?', (ride_id,))
    row = cursor.fetchone()
    conn.close()
    if row is None:
        return None
    return {
        "ride_id": row[0],
        "timestamp": row[1],
        "duration": row[2],
        "avg_power": row[3],
        "avg_heart_rate": row[4],
        "avg_cadence": row[5],
        "max_power": row[6],
        "max_heart_rate": row[7],
        "max_cadence": row[8],
        "distance": row[9],
        "energy_output": row[10],
        "training_stress_score": row[11],
        "time_in_zones": {
            "Z1": row[12],
            "Z2": row[13],
            "Z3": row[14],
            "Z4": row[15],
            "Z5": row[16],
            "Z6": row[17],
        },
        "pedal_balance": row[18]
    }
