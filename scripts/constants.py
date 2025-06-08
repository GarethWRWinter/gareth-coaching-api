# scripts/constants.py
import os

# Load FTP from environment variable (set in Render dashboard)
FTP = float(os.getenv("FTP", 308))  # Default to 308 if not set

# Log for verification
print(f"🚴‍♂️ Loaded FTP: {FTP} watts (from environment or default)")
