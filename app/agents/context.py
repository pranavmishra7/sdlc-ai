from typing import Any, Dict
from dataclasses import asdict, is_dataclass


def serialize_context(context: Any) -> Dict[str, Any]:
    """
    Normalize ANY context type into a dict that agents can consume.
    This is the single source of truth for context handling.
    """

    # 1️⃣ Already a dict → OK
    if isinstance(context, dict):
        return context

    # 2️⃣ Raw string → wrap it
    if isinstance(context, str):
        return {
            "text": context
        }

    # 3️⃣ Dataclass (e.g., SDLCState)
    if is_dataclass(context):
        return asdict(context)

    # 4️⃣ Object with __dict__ (models, state objects)
    if hasattr(context, "__dict__"):
        return {
            k: v for k, v in vars(context).items()
            if not k.startswith("_")
        }

    # 5️⃣ Last resort → string fallback
    return {
        "value": str(context)
    }
