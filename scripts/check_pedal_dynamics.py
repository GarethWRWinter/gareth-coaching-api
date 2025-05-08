from fitparse import FitFile
from pathlib import Path

# Path to most recent FIT file
fit_file_path = Path(__file__).resolve().parents[1] / "data" / "2025-05-01-064707-ELEMNT BOLT 5F01-229-0.fit"

fitfile = FitFile(str(fit_file_path))
field_counts = {}

# Scan all fields in "record" messages
for record in fitfile.get_messages("record"):
    for field in record:
        name = field.name
        field_counts[name] = field_counts.get(name, 0) + 1

# List of pedal-related fields to check
pedal_fields = [
    "left_right_balance",
    "left_pedal_smoothness", "right_pedal_smoothness",
    "left_torque_effectiveness", "right_torque_effectiveness",
    "platform_center_offset"
]

print(f"\n📊 Checking pedal dynamics in: {fit_file_path.name}\n")

found = False
for field in pedal_fields:
    if field in field_counts:
        print(f"✅ {field}: {field_counts[field]} records")
        found = True
    else:
        print(f"❌ {field}: not found")

if not found:
    print("\nℹ️ No pedal dynamics recorded in this ride — likely from your turbo setup.")
