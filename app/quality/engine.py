from app.quality.contracts import QUALITY_CONTRACTS
from app.quality.validator import validate
from app.quality.scorer import score


def assess(step: str, parsed: dict | None) -> dict:
    errors = validate(step, parsed)
    s = score(parsed or {}, errors)

    return {
        "score": s,
        "passed": s >= QUALITY_CONTRACTS[step]["min_score"],
        "errors": errors,
    }
