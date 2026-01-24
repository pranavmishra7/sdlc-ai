def score_quality(section: str, content: dict, validation_errors: list[str]) -> dict:
    score = 100

    # Structural penalties
    score -= len(validation_errors) * 10

    # Shallow content penalty
    for value in content.values():
        if isinstance(value, list) and len(value) == 1:
            score -= 5

    score = max(score, 0)

    rating = "EXCELLENT" if score >= 85 else "GOOD" if score >= 70 else "WEAK"

    return {
        "score": score,
        "rating": rating,
        "issues": validation_errors,
    }


def confidence_level(score: int) -> str:
    if score >= 85:
        return "HIGH"
    if score >= 70:
        return "MEDIUM"
    return "LOW"


def detect_gaps(section: str, content: dict) -> list[str]:
    gaps = []

    if section == "architecture" and "security" not in str(content).lower():
        gaps.append("Security considerations not explicitly addressed")

    if section == "estimation" and "buffer" not in str(content).lower():
        gaps.append("No contingency or buffer mentioned")

    if section == "sow" and "assumptions" not in content:
        gaps.append("Commercial assumptions missing")

    return gaps
