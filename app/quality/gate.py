# app/quality/gate.py

from app.quality.contracts import QUALITY_CONTRACTS
from app.quality.validator import validate_structure
from app.quality.scorer import score_quality


def run_quality_gate(step: str, output: dict) -> dict:
    contract = QUALITY_CONTRACTS.get(step)

    if not contract:
        return {"status": "PASS", "score": 100}

    raw = output.get("raw")
    parsed = output.get("parsed")

    errors = validate_structure(parsed, contract)
    score = score_quality(raw, contract.get("min_words", 0))

    status = "PASS"
    if errors or score < 60:
        status = "FAIL"

    return {
        "status": status,
        "score": score,
        "errors": errors,
    }
