# scripts/migrations/create_athletes_table.py

from sqlalchemy import create_engine, text

# Path to your local SQLite database
DATABASE_URL = "sqlite:///ride_data.db"

def create_athletes_table():
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS athletes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ftp FLOAT DEFAULT 308.0
            );
        """))
        print("✅ athletes table created successfully.")

if __name__ == "__main__":
    create_athletes_table()
