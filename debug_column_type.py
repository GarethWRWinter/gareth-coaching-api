# debug_column_type.py

from sqlalchemy import create_engine, inspect
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost/dbname")
engine = create_engine(DATABASE_URL)

insp = inspect(engine)
columns = insp.get_columns("rides")
for col in columns:
    if col["name"] == "power_zone_times":
        print(f"Column 'power_zone_times' type: {col['type']}")
