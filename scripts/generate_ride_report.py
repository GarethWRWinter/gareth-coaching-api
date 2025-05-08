import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
from pathlib import Path

# === Config ===
DATA_FOLDER = Path(__file__).resolve().parents[1] / "data"
RIDE_FILE = DATA_FOLDER / "parsed_full_metrics.csv"
LOG_FILE = DATA_FOLDER / "ride_history.csv"
PDF_FILE = DATA_FOLDER / "ride_report.pdf"

# === Load Data ===
df = pd.read_csv(RIDE_FILE, parse_dates=["timestamp"])
summary = pd.read_csv(LOG_FILE)
latest = summary.iloc[-1]  # Get most recent ride log

# === Create Plots ===
plt.style.use("ggplot")

# Power plot
plt.figure(figsize=(10, 3))
df["power"].plot(title="Power Over Time", ylabel="Watts")
plt.tight_layout()
plt.savefig(DATA_FOLDER / "power_plot.png")
plt.close()

# HR plot
if "heart_rate" in df.columns:
    plt.figure(figsize=(10, 3))
    df["heart_rate"].plot(title="Heart Rate Over Time", ylabel="bpm", color="red")
    plt.tight_layout()
    plt.savefig(DATA_FOLDER / "hr_plot.png")
    plt.close()

# Zone pie chart
zones = ["Z1", "Z2", "Z3", "Z4", "Z5", "Z6", "Z7"]
zone_secs = latest[zones].fillna(0)
plt.figure(figsize=(6, 6))
plt.pie(zone_secs, labels=zones, autopct="%1.1f%%")
plt.title("Time in Power Zones")
plt.savefig(DATA_FOLDER / "zones_plot.png")
plt.close()

# === Create PDF ===
pdf = FPDF()
pdf.set_auto_page_break(auto=True, margin=15)
pdf.add_page()

# Header
pdf.set_font("Arial", "B", 16)
pdf.cell(0, 10, "Cycling Ride Report", ln=True)

# Metadata
pdf.set_font("Arial", size=12)
pdf.cell(0, 10, f"File: {latest['filename']}", ln=True)
pdf.cell(0, 10, f"Date: {latest['date']}", ln=True)

# Metrics
pdf.cell(0, 10, f"Normalized Power (NP): {latest['NP']} W", ln=True)
pdf.cell(0, 10, f"Intensity Factor (IF): {latest['IF']}", ln=True)
pdf.cell(0, 10, f"Training Stress Score (TSS): {latest['TSS']}", ln=True)

# Time in Zones Table
pdf.ln(5)
pdf.set_font("Arial", "B", 12)
pdf.cell(0, 10, "Time in Zones (seconds):", ln=True)
pdf.set_font("Arial", size=12)
for zone in zones:
    val = int(latest[zone]) if not pd.isna(latest[zone]) else 0
    pdf.cell(0, 10, f"{zone}: {val} sec", ln=True)

# Insert charts
pdf.ln(5)
for img in ["power_plot.png", "hr_plot.png", "zones_plot.png"]:
    img_path = DATA_FOLDER / img
    if img_path.exists():
        pdf.image(str(img_path), w=180)
        pdf.ln(5)

# Save PDF
pdf.output(str(PDF_FILE))
print(f"\n✅ Saved: {PDF_FILE.name}")
