import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import numpy as np

# === Config ===
st.set_page_config(layout="wide")
st.title("🚴 Gareth's Ride Data Dashboard")

# === Locate and load data ===
DATA_FOLDER = Path(__file__).resolve().parents[1] / "data"
ride_files = list(DATA_FOLDER.glob("*.csv"))

if not ride_files:
    st.error("No ride data found in /data folder.")
    st.stop()

# === Ride comparison selection ===
st.sidebar.title("📂 Ride Selection")
ride_file_1 = st.sidebar.selectbox("Primary Ride:", [f.name for f in ride_files], index=0)
ride_file_2 = st.sidebar.selectbox("Compare to (optional):", ["None"] + [f.name for f in ride_files], index=0)

# === Load primary ride ===
df1 = pd.read_csv(DATA_FOLDER / ride_file_1, parse_dates=["timestamp"])

# === Load comparison ride if selected ===
df2 = None
if ride_file_2 != "None" and ride_file_2 != ride_file_1:
    df2 = pd.read_csv(DATA_FOLDER / ride_file_2, parse_dates=["timestamp"])

# === Choose metrics to plot ===
available_metrics = ['power', 'heart_rate', 'cadence', 'speed']
selected = st.multiselect("Metrics to show:", available_metrics, default=available_metrics)

# === Define FTP and Power Zones ===
FTP = 280
zones = {
    'Z1 Active Recovery': (0, 0.55 * FTP),
    'Z2 Endurance': (0.56 * FTP, 0.75 * FTP),
    'Z3 Tempo': (0.76 * FTP, 0.90 * FTP),
    'Z4 Threshold': (0.91 * FTP, 1.05 * FTP),
    'Z5 VO2 Max': (1.06 * FTP, 1.20 * FTP),
    'Z6 Anaerobic': (1.21 * FTP, 1.50 * FTP),
    'Z7 Neuromuscular': (1.51 * FTP, 2000)
}

# === Summary Metrics Function ===
def compute_summary(df):
    df_power = df.dropna(subset=['power']).copy()
    duration_sec = (df_power['timestamp'].iloc[-1] - df_power['timestamp'].iloc[0]).total_seconds()
    np_power = (df_power['power'] ** 4).mean() ** 0.25
    intensity_factor = np_power / FTP
    tss = (duration_sec * np_power * intensity_factor) / (FTP * 3600) * 100
    return duration_sec, np_power, intensity_factor, tss

# === Show summary metrics ===
st.subheader("📊 Ride Summary")
col1, col2 = st.columns(2)

with col1:
    st.markdown(f"### 📌 {ride_file_1}")
    dur1, np1, if1, tss1 = compute_summary(df1)
    st.metric("NP", f"{np1:.0f} W")
    st.metric("IF", f"{if1:.2f}")
    st.metric("TSS", f"{tss1:.1f}")
    st.metric("Duration", f"{int(dur1 // 60)} min")

if df2 is not None:
    with col2:
        st.markdown(f"### 🔄 {ride_file_2}")
        dur2, np2, if2, tss2 = compute_summary(df2)
        st.metric("NP", f"{np2:.0f} W")
        st.metric("IF", f"{if2:.2f}")
        st.metric("TSS", f"{tss2:.1f}")
        st.metric("Duration", f"{int(dur2 // 60)} min")

# === Power Zone Distribution Bar Chart ===
def plot_zone_chart(df, title):
    df_power = df.dropna(subset=['power'])
    zone_durations = []
    for name, (z_min, z_max) in zones.items():
        zone_time = df_power[(df_power['power'] >= z_min) & (df_power['power'] < z_max)].shape[0]
        zone_durations.append((name, zone_time))
    zone_df = pd.DataFrame(zone_durations, columns=['Zone', 'Seconds'])
    return px.bar(zone_df, x='Zone', y='Seconds', title=title, text='Seconds')

st.subheader("🟩 Power Zone Comparison")
fig1 = plot_zone_chart(df1, f"Zones: {ride_file_1}")
st.plotly_chart(fig1, use_container_width=True)

if df2 is not None:
    fig2 = plot_zone_chart(df2, f"Zones: {ride_file_2}")
    st.plotly_chart(fig2, use_container_width=True)

# === Time Series Plot ===
st.subheader("📈 Ride Metrics Over Time")
if selected:
    fig = go.Figure()
    for metric in selected:
        if metric in df1.columns:
            fig.add_trace(go.Scatter(
                x=df1['timestamp'],
                y=df1[metric],
                mode='lines',
                name=f"{metric} - {ride_file_1}"
            ))
        if df2 is not None and metric in df2.columns:
            fig.add_trace(go.Scatter(
                x=df2['timestamp'],
                y=df2[metric],
                mode='lines',
                name=f"{metric} - {ride_file_2}"
            ))
    fig.update_layout(
        height=600,
        xaxis_title="Time",
        yaxis_title="Metric Value",
        legend_title="Metric",
        template="plotly_white"
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Select at least one metric to display.")
