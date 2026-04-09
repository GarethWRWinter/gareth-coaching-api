# Coggan 7-Zone Power Model (as fractions of FTP)
POWER_ZONES = {
    "Z1": {"name": "Active Recovery", "low": 0.00, "high": 0.55},
    "Z2": {"name": "Endurance", "low": 0.56, "high": 0.75},
    "Z3": {"name": "Tempo", "low": 0.76, "high": 0.90},
    "Z4": {"name": "Threshold", "low": 0.91, "high": 1.05},
    "Z5": {"name": "VO2max", "low": 1.06, "high": 1.20},
    "Z6": {"name": "Anaerobic", "low": 1.21, "high": 1.50},
    "Z7": {"name": "Neuromuscular", "low": 1.51, "high": 3.00},
}

# Heart Rate Zones (as fractions of max HR or HRR)
HR_ZONES = {
    "Z1": {"name": "Recovery", "low": 0.50, "high": 0.60},
    "Z2": {"name": "Endurance", "low": 0.60, "high": 0.70},
    "Z3": {"name": "Tempo", "low": 0.70, "high": 0.80},
    "Z4": {"name": "Threshold", "low": 0.80, "high": 0.90},
    "Z5": {"name": "VO2max", "low": 0.90, "high": 1.00},
}

# CTL/ATL time constants (days)
CTL_TIME_CONSTANT = 42
ATL_TIME_CONSTANT = 7

# Normalized Power rolling window (seconds)
NP_ROLLING_WINDOW = 30

# Training Stress thresholds
TSB_OVERTRAINING_THRESHOLD = -25
RAMP_RATE_WARNING_THRESHOLD = 7.0  # TSS/day per week

# FTP estimation multipliers
FTP_FROM_20MIN_MULTIPLIER = 0.95
FTP_FROM_5MIN_MULTIPLIER = 0.75
FTP_FROM_8MIN_MULTIPLIER = 0.90

# Best effort durations (seconds) for power profile — TrainingPeaks-style intervals
POWER_PROFILE_DURATIONS = {
    "5s": 5,
    "10s": 10,
    "15s": 15,
    "30s": 30,
    "1min": 60,
    "2min": 120,
    "5min": 300,
    "10min": 600,
    "20min": 1200,
    "30min": 1800,
    "60min": 3600,
    "90min": 5400,
}

# Rider type classification thresholds (W/kg at specific durations)
# Based on Coggan's power profile chart, simplified
RIDER_TYPE_THRESHOLDS = {
    "sprinter": {"duration": 5, "min_wpkg": 15.0},
    "pursuiter": {"duration": 300, "min_wpkg": 5.0},
    "time_trialist": {"duration": 1200, "min_wpkg": 4.5},
    "climber": {"duration": 3600, "min_wpkg": 4.0},
}

# Rider profile categories for radar chart — 5 energy systems
RIDER_PROFILE_CATEGORIES = {
    "sprint": {"duration": 5, "label": "Sprint (5s)"},
    "anaerobic": {"duration": 60, "label": "Anaerobic (1min)"},
    "vo2max": {"duration": 300, "label": "VO2max (5min)"},
    "threshold": {"duration": 1200, "label": "Threshold (20min)"},
    "endurance": {"duration": 3600, "label": "Endurance (60min)"},
}

# Power benchmarks (W/kg) for radar chart scoring — Coggan-based
# Each list represents 9 levels from untrained to world-class
POWER_BENCHMARKS_WPKG = {
    5:    [8.0, 10.0, 12.0, 14.0, 16.0, 18.0, 20.0, 22.0, 24.0],
    60:   [3.0, 4.0, 5.0, 5.5, 6.5, 7.0, 8.0, 9.0, 11.0],
    300:  [2.0, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 7.0],
    1200: [1.5, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.5],
    3600: [1.0, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 6.0],
}
