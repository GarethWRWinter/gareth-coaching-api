import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import argparse

# ✅ Add parent directory to path to import models.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models import Base, FTPRecord

# Set up database
engine = create_engine("sqlite:///ride_data.db")
Base.metadata.create_all(bind=engine)
Session = sessionmaker(bind=engine)
session = Session()

# Argument parser for CLI
parser = argparse.ArgumentParser(description="Add or fetch FTP records.")
parser.add_argument("--set", type=float, help="Set a new FTP value (e.g., --set 260)")
parser.add_argument("--source", type=str, default="manual", help="Source of FTP (default: manual)")
parser.add_argument("--latest", action="store_true", help="Print the latest FTP value")
args = parser.parse_args()

if args.set:
    new_ftp = FTPRecord(
        ftp=args.set,
        date=datetime.now(),
        source=args.source
    )
    session.add(new_ftp)
    session.commit()
    print(f"✅ FTP set to {args.set} watts (source: {args.source})")

if args.latest:
    latest_ftp = (
        session.query(FTPRecord)
        .order_by(FTPRecord.date.desc())
        .first()
    )
    if latest_ftp:
        print(f"📈 Latest FTP: {latest_ftp.ftp} watts (set on {latest_ftp.date.date()}, source: {latest_ftp.source})")
    else:
        print("⚠️ No FTP records found.")
