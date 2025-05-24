# scripts/sanitize.py

import math
import pandas as pd
import numpy as np

def sanitize(obj):
    if isinstance(obj, dict):
        return {k: sanitize(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [sanitize(v) for v in obj]
    elif isinstance(obj, (pd.Timestamp, np.datetime64)):
        return str(obj)
    elif isinstance(obj, (pd.Series, np.ndarray)):
        return sanitize(obj.tolist())
    elif isinstance(obj, float):
        if math.isinf(obj) or math.isnan(obj):
            return None
        return round(obj, 2)
    elif isinstance(obj, (pd.Int64Dtype, np.integer)):
        return int(obj)
    elif isinstance(obj, (pd.Float64Dtype, np.floating)):
        return float(obj)
    return obj
