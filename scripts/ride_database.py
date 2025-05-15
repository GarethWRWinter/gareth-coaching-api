import sqlite3
from models.pydantic_models import RideSummary

def save_ride_summary(summary: RideSummary):
    conn = sqlite3.connect("ride_data.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS ride_summaries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            duration_sec INTEGER,
            avg_power REAL,
            max_power INTEGER,
            avg_hr REAL,
            max_hr INTEGER,
            avg_cadence REAL,
            max_cadence INTEGER,
            distance_km REAL,
            total_work_kj REAL,
            time_in_zones TEXT
        )
        """
    )

    cursor.execute(
        """
        INSERT INTO ride_summaries (
            date,
            duration_sec,
            avg_power,
            max_power,
            avg_hr,
            max_hr,
            avg_cadence,
            max_cadence,
            distance_km,
            total_work_kj,
            time_in_zones
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            summary.date,
            summary.duration_sec,
            summary.avg_power,
            summary.max_power,
            summary.avg_hr,
            summary.max_hr,
            summary.avg_cadence,
            summary.max_cadence,
            summary.distance_km,
            summary.total_work_kj,
            str(summary.time_in_zones),
        ),
    )

    conn.commit()
    conn.close()
