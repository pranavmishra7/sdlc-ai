from app.state.sdlc_state import SDLCState
from app.agents.intake_agent import run_intake


def intake_node(state: SDLCState) -> SDLCState:
    result = run_intake(state.product_idea)

    # result must already be:
    # { "type": ..., "raw": ..., "parsed": ... }

    return state.complete_step("intake", result)
