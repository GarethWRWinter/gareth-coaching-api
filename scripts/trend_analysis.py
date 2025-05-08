import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# === Config ===
st.set_page_config(layout="wide")
st.title("📆 Training Trend Analysis")

# === Load historical ride log ===
DATA_FOLDER = Path(__file__).resolve().parents[1] / "data"
LOG_FILE = DATA_FOLDER / "ride_history.csv"

if not LOG_FILE.exists():
    st.error("No ride history found. Run log_ride_to_history.py first.")
    st.stop()

df = pd.read_csv(LOG_FILE, parse_dates=["date"])
df['week'] = df['date'].dt.to_period('W').apply(lambda r: r.start_time)
df['month'] = df['date'].dt.to_period('M').apply(lambda r: r.start_time)

# === Filters ===
st.sidebar.header("🔍 Filters")
time_range = st.sidebar.selectbox("Group by:", ["Week", "Month"])
group_col = 'week' if time_range == 'Week' else 'month'

# === Summary Charts ===
st.subheader(f"📊 Average Metrics by {time_range}")
agg_df = df.groupby(group_col).agg({
    "NP": "mean",
    "IF": "mean",
    "TSS": "sum"
}).reset_index()

col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(px.line(agg_df, x=group_col, y="NP", title=f"⚡ Normalized Power ({time_range})"), use_container_width=True)
    st.plotly_chart(px.line(agg_df, x=group_col, y="IF", title=f"🔥 Intensity Factor ({time_range})"), use_container_width=True)
with col2:
    st.plotly_chart(px.bar(agg_df, x=group_col, y="TSS", title=f"📈 Total TSS ({time_range})"), use_container_width=True)

# === Ride Count ===
st.subheader(f"🚴 Ride Count per {time_range}")
count_df = df.groupby(group_col).size().reset_index(name='ride_count')
st.plotly_chart(px.bar(count_df, x=group_col, y='ride_count', title=f"🏁 Rides Per {time_range}"), use_container_width=True)
