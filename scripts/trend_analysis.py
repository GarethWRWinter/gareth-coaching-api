import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine

# Connect to the database
engine = create_engine("sqlite:///ride_data.db")

# Load power zone data
df_power = pd.read_sql_table("time_in_zone", engine)

# Extract date from filename
df_power["date"] = pd.to_datetime(df_power["filename"].str.extract(r"(\d{4}-\d{2}-\d{2})")[0])

# Pivot table for power zones
pivot_power = df_power.pivot_table(index="date", columns="zone", values="seconds", aggfunc="sum")

# Plot power zones
pivot_power.plot(kind="bar", stacked=True, figsize=(12, 6), title="Time in Power Zones Over Time")
plt.ylabel("Seconds")
plt.xlabel("Ride Date")
plt.tight_layout()
plt.show()

# Load HR zone data
df_hr = pd.read_sql_table("hr_time_in_zone", engine)
df_hr["date"] = pd.to_datetime(df_hr["filename"].str.extract(r"(\d{4}-\d{2}-\d{2})")[0])
pivot_hr = df_hr.pivot_table(index="date", columns="zone", values="seconds", aggfunc="sum")

# Plot HR zones
pivot_hr.plot(kind="bar", stacked=True, figsize=(12, 6), title="Time in Heart Rate Zones Over Time")
plt.ylabel("Seconds")
plt.xlabel("Ride Date")
plt.tight_layout()
plt.show()
