from sqlalchemy import create_engine, text

DATABASE_URL = "sqlite:///ride_data.db"  # adjust if needed
engine = create_engine(DATABASE_URL)

def update_ftp(new_ftp):
    with engine.connect() as connection:
        connection.execute(text("UPDATE athletes SET ftp = :ftp"), {"ftp": new_ftp})
        print(f"✅ FTP updated to {new_ftp} watts.")

if __name__ == "__main__":
    # Replace 308.0 with your actual FTP if needed
    update_ftp(308.0)
