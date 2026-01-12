from app.state.sdlc_state import SDLCState
from app.agents.risk_agent import run_risk


def risk_node(state: SDLCState) -> SDLCState:
    context = state.get_context()

    agent_result = run_risk(context)

    output = {
        "type": "text",
        "raw": agent_result["raw_output"],
        "parsed": None,
    }

    return state.complete_step("risk", output)
