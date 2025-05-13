import numpy as np

def sanitize(value):
    if isinstance(value, (np.int64, np.int32)):
        return int(value)
    elif isinstance(value, (np.float64, np.float32)):
        return float(value)
    elif isinstance(value, (np.bool_)):
        return bool(value)
    return value

def sanitize_dict(d):
    if isinstance(d, dict):
        return {k: sanitize_dict(v) for k, v in d.items()}
    elif isinstance(d, list):
        return [sanitize_dict(i) for i in d]
    else:
        return sanitize(d)
