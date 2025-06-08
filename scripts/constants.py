# scripts/constants.py
import os

# Load FTP from environment variable set in Render
FTP = float(os.getenv("FTP", 308))  # default to 308 if not set

# Logging for diagnosis
print(f"[INFO] Using FTP (Functional Threshold Power): {FTP} watts")
