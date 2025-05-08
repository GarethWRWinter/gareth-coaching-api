import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine
from models import Base, RideData
from fitparse import FitFile

load_dotenv()

DROPBOX_FOLDER = os.getenv("DROPBOX_FOLDER", "/WahooFitness")
LATEST_FILE = "latest_ride.fit"
CSV_FILE = "latest_ride.csv"
DB_PATH = "ride_data.db"

def find_latest_fit_file(folder):
    files = [f for f in os.listdir(folder) if f.endswith(".fit")]
    files.sort(reverse=True)
    return os.path.join(folder, files[0]) if files else None

def parse_fit_file_to_df(file_path):
    fitfile = FitFile(file_path)
    data = []
    for record in fitfile.get_messages("record"):
        row = {}
        for field in record:
            row[field.name] = field.value
        if row:
            data.append(row)
    return pd.DataFrame(data)

def save_to_db(df, filename):
    engine = create_engine(f"sqlite:///{DB_PATH}")
    Base.metadata.create_all(engine)

    ride_records = [
        RideData(
            timestamp=row.get("timestamp"),
            power=row.get("power"),
            heart_rate=row.get("heart_rate"),
            cadence=row.get("cadence"),
            speed=row.get("speed"),
            distance=row.get("distance"),
            altitude=row.get("altitude"),
            temperature=row.get("temperature"),
            left_right_balance=row.get("left_right_balance"),
            filename=filename
        )
        for _, row in df.iterrows()
    ]

    with engine.begin() as conn:
        conn.execute(RideData.__table__.delete().where(RideData.filename == filename))  # Prevent duplicates
        conn.execute(RideData.__table__.insert(), [r.__dict__ for r in ride_records])

def main():
    folder = "rides"
    latest_fit = find_latest_fit_file(folder)
    if not latest_fit:
        print("❌ No .fit files found.")
        return

    df = parse_fit_file_to_df(latest_fit)
    filename = os.path.basename(latest_fit)
    save_to_db(df, filename)

    df.to_csv(CSV_FILE, index=False)
    print(f"✅ Saved {len(df)} records from {filename} to {DB_PATH}")
    print(f"📁 Also saved {CSV_FILE} for zone analysis")

if __name__ == "__main__":
    main()
