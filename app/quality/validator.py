from app.quality.contracts import QUALITY_CONTRACTS


def validate_structure(step: str, parsed: dict | None) -> list[str]:
    if not isinstance(parsed, dict):
        return ["Parsed output is missing or invalid"]

    required = QUALITY_CONTRACTS[step]["required_keys"]
    errors = []

    for key in required:
        if key not in parsed or not parsed[key]:
            errors.append(f"Missing or empty field: {key}")

    return errors
