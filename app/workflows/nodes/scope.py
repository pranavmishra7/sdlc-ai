from app.state.sdlc_state import SDLCState
from app.agents.scope_agent import run_scope


def scope_node(state: SDLCState) -> SDLCState:
    context = state.get_context()

    agent_result = run_scope(context)

    output = {
        "type": "text",
        "raw": agent_result["raw_output"],
        "parsed": None,
    }

    return state.complete_step("scope", output)
