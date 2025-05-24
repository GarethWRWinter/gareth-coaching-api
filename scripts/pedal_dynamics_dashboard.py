import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# === Config ===
st.set_page_config(layout="wide")
st.title("🦵 Pedal Dynamics Analysis")

# === Load Data ===
DATA_FOLDER = Path(__file__).resolve().parents[1] / "data"
FILE = DATA_FOLDER / "parsed_full_metrics.csv"

if not FILE.exists():
    st.error("No parsed ride data found. Run parse_full_fit.py first.")
    st.stop()

df = pd.read_csv(FILE, parse_dates=['timestamp'])

# === Detect Available Pedal Metrics ===
pedal_fields = [
    "left_right_balance",
    "left_torque_effectiveness", "right_torque_effectiveness",
    "left_pedal_smoothness", "right_pedal_smoothness",
    "platform_center_offset"
]

available = [col for col in pedal_fields if col in df.columns]
if not available:
    st.warning("❌ No pedal dynamics recorded in this ride.")
    st.stop()

st.success(f"✅ Found: {', '.join(available)}")

# === Visuals ===
if "left_right_balance" in available:
    fig = px.line(df, x="timestamp", y="left_right_balance", title="🔄 Left/Right Power Balance")
    st.plotly_chart(fig, use_container_width=True)

if "left_torque_effectiveness" in available and "right_torque_effectiveness" in available:
    fig = px.line(df, x="timestamp", y=["left_torque_effectiveness", "right_torque_effectiveness"],
                  title="🎯 Torque Effectiveness (L vs R)")
    st.plotly_chart(fig, use_container_width=True)

if "left_pedal_smoothness" in available and "right_pedal_smoothness" in available:
    fig = px.line(df, x="timestamp", y=["left_pedal_smoothness", "right_pedal_smoothness"],
                  title="🧼 Pedal Smoothness (L vs R)")
    st.plotly_chart(fig, use_container_width=True)

if "platform_center_offset" in available:
    fig = px.line(df, x="timestamp", y="platform_center_offset", title="🦶 Platform Center Offset")
    st.plotly_chart(fig, use_container_width=True)
