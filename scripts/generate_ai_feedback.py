import pandas as pd
from openai import OpenAI
from pathlib import Path
import os

# === Config ===
DATA_FOLDER = Path(__file__).resolve().parents[1] / "data"
LOG_FILE = DATA_FOLDER / "ride_history.csv"
FEEDBACK_FILE = DATA_FOLDER / "ride_feedback.txt"

# Set your OpenAI API key (or use environment variable)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not set in environment variables")

client = OpenAI(api_key=OPENAI_API_KEY)

# === Load Latest Ride ===
df = pd.read_csv(LOG_FILE)
latest = df.iloc[-1]

# === Create Prompt ===
prompt = f"""
You are an elite cycling coach.
Generate a short personalized analysis based on the following ride data:

Filename: {latest['filename']}
Date: {latest['date']}
NP: {latest['NP']} W
IF: {latest['IF']}
TSS: {latest['TSS']}
Time in Zones (seconds):
Z1: {latest['Z1']}
Z2: {latest['Z2']}
Z3: {latest['Z3']}
Z4: {latest['Z4']}
Z5: {latest['Z5']}
Z6: {latest['Z6']}
Z7: {latest['Z7']}

Give feedback in 3–4 bullet points:
- Start with what the rider did well
- Mention any potential red flags or missed opportunities
- Suggest next steps for tomorrow’s training
- Keep tone motivating, clear, and professional
"""

# === Get Response ===
response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are a world-class cycling coach."},
        {"role": "user", "content": prompt}
    ]
)

feedback = response.choices[0].message.content

# === Save Feedback ===
with open(FEEDBACK_FILE, "w") as f:
    f.write(feedback)

print("\n✅ Saved AI feedback to ride_feedback.txt")
