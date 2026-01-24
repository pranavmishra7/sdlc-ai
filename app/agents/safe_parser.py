import json
import re


def safe_parse_json(text):
    # 🚑 If LLM already returned parsed JSON
    if isinstance(text, dict):
        return text

    if not isinstance(text, str):
        return None

    text = text.strip()
    if not text:
        return None

    # Try strict parse
    try:
        return json.loads(text)
    except Exception:
        pass

    # Remove markdown fences
    text = re.sub(r"```(?:json)?|```", "", text, flags=re.IGNORECASE).strip()

    # Extract first JSON object
    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        return None

    try:
        return json.loads(match.group())
    except Exception:
        return None
