from sqlalchemy import create_engine, text

# Use the correct database URL here
# Example: for SQLite local file
DATABASE_URL = "sqlite:///ride_data.db"
# Example for Postgres:
# DATABASE_URL = "postgresql://username:password@localhost:5432/yourdb"

engine = create_engine(DATABASE_URL)

def add_ftp_column():
    with engine.connect() as conn:
        # Check if the column already exists (SQLite-specific)
        result = conn.execute(text("""
            PRAGMA table_info(athletes);
        """))
        columns = [row[1] for row in result]
        if "ftp" in columns:
            print("✅ 'ftp' column already exists in 'athletes' table.")
            return

        # Add the column
        conn.execute(text("""
            ALTER TABLE athletes ADD COLUMN ftp FLOAT DEFAULT 308.0;
        """))
        print("✅ 'ftp' column added to 'athletes' table with default 308.0 watts.")

if __name__ == "__main__":
    add_ftp_column()
