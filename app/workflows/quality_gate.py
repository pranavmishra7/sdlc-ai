from app.quality.engine import assess
from app.state.sdlc_state import SDLCJobStatus


def apply_quality_gate(state, step: str, parsed: dict):
    """
    Enforces quality contract for a step.
    Mutates state if failed.
    """

    result = assess(step, parsed)

    state.quality[step] = result

    if not result["passed"]:
        raise RuntimeError(f"Quality gate failed for {step}: {result['errors']}")

    return state
