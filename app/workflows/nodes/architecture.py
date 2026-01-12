from app.state.sdlc_state import SDLCState
from app.agents.architecture_agent import run_architecture


def architecture_node(state: SDLCState) -> SDLCState:
    context = state.get_context()

    agent_result = run_architecture(context)

    output = {
        "type": "text",
        "raw": agent_result["raw_output"],
        "parsed": None,
    }

    return state.complete_step("architecture", output)
