from typing import Dict, Any

def compact(obj: Dict[str, Any], max_items: int = 5) -> Dict[str, Any]:
    """
    Reduce list sizes in dict values to limit prompt size.
    Does NOT mutate the original object.
    """
    if not isinstance(obj, dict):
        return obj

    return {
        k: (v[:max_items] if isinstance(v, list) else v)
        for k, v in obj.items()
    }
