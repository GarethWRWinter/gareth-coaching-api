import numpy as np
import pandas as pd

def sanitize_value(value):
    if isinstance(value, (np.generic, pd.Timestamp)):
        return value.item() if hasattr(value, "item") else str(value)
    elif isinstance(value, (list, tuple)):
        return [sanitize_value(v) for v in value]
    elif isinstance(value, dict):
        return {k: sanitize_value(v) for k, v in value.items()}
    else:
        return value

def sanitize_dict(data: dict) -> dict:
    return sanitize_value(data)
