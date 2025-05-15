def sanitize(obj):
    if isinstance(obj, dict):
        return {k: sanitize(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [sanitize(v) for v in obj]
    elif hasattr(obj, 'item'):
        return obj.item()
    else:
        return obj


def sanitize_dict(d: dict) -> dict:
    return sanitize(d)
