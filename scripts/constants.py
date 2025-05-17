# scripts/constants.py

FTP = 308  # watts – Gareth's current FTP

POWER_ZONES = [
    {"name": "Z1 - Active Recovery", "min": 0, "max": 0.55 * FTP},
    {"name": "Z2 - Endurance", "min": 0.55 * FTP, "max": 0.75 * FTP},
    {"name": "Z3 - Tempo", "min": 0.75 * FTP, "max": 0.90 * FTP},
    {"name": "Z4 - Threshold", "min": 0.90 * FTP, "max": 1.05 * FTP},
    {"name": "Z5 - VO2 Max", "min": 1.05 * FTP, "max": 1.20 * FTP},
    {"name": "Z6 - Anaerobic", "min": 1.20 * FTP, "max": 1.50 * FTP},
    {"name": "Z7 - Neuromuscular", "min": 1.50 * FTP, "max": float("inf")}
]
