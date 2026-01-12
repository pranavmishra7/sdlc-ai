from app.state.sdlc_state import SDLCState
from app.agents.estimation_agent import run_estimation


def estimation_node(state: SDLCState) -> SDLCState:
    context = state.get_context()

    agent_result = run_estimation(context)

    output = {
        "type": "text",
        "raw": agent_result["raw_output"],
        "parsed": None,
    }

    return state.complete_step("estimation", output)
