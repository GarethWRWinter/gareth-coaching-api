# scripts/constants.py
import os

# Load FTP from environment variable (set in Render)
FTP = float(os.getenv("FTP", 308))  # Use default 308 if not set
