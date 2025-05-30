import sqlite3
from typing import List, Dict


def get_all_rides() -> List[Dict]:
    conn = sqlite3.connect("ride_data.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM rides")
    columns = [col[0] for col in cursor.description]
    rows = cursor.fetchall()
    conn.close()

    rides = []
    for row in rows:
        rides.append(dict(zip(columns, row)))
    return rides
