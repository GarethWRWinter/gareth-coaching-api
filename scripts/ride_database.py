import sqlite3
from typing import Any, Dict, List
import os
from scripts.sanitize import sanitize_dict

DB_PATH = os.path.join(os.path.dirname(__file__), "../ride_data.db")

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ride_summaries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                filename TEXT,
                summary TEXT
            )
        """)
        conn.commit()

def save_ride_summary(filename: str, summary: Dict[str, Any]) -> None:
    init_db()
    summary_clean = sanitize_dict(summary)
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO ride_summaries (timestamp, filename, summary)
            VALUES (datetime('now'), ?, ?)
        """, (filename, str(summary_clean)))
        conn.commit()

def fetch_ride_history(limit: int = 10) -> List[Dict[str, Any]]:
    init_db()
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT timestamp, filename, summary
            FROM ride_summaries
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()

    return [
        {"timestamp": row[0], "filename": row[1], "summary": row[2]}
        for row in rows
    ]
