# scripts/visualize_latest_ride.py

import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

# Connect to database
conn = sqlite3.connect("ride_data.db")

# Read data
df = pd.read_sql_query("SELECT * FROM ride_data ORDER BY timestamp", conn)
conn.close()

# Parse timestamp to datetime
df["timestamp"] = pd.to_datetime(df["timestamp"])

# Plot Power, Heart Rate, and Cadence
plt.figure(figsize=(15, 5))
plt.plot(df["timestamp"], df["power"], label="Power (W)")
plt.plot(df["timestamp"], df["heart_rate"], label="Heart Rate (bpm)")
plt.plot(df["timestamp"], df["cadence"], label="Cadence (rpm)")
plt.legend()
plt.xlabel("Time")
plt.ylabel("Value")
plt.title("Latest Ride Overview")
plt.grid(True)
plt.tight_layout()
plt.show()
