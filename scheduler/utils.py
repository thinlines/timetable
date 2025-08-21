import json

def coerce_json(value):
    """Return Python obj from a value that might be a JSON string or already a Python object."""
    if value is None:
        return None
    if isinstance(value, (dict, list)):
        return value
    # assume string
    return json.loads(value)