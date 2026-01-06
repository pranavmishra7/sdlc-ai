from app.state.sdlc_state import SDLCState
from app.agents.sow_agent import run_sow

def sow_node(state: SDLCState) -> SDLCState:
    state.sow = run_sow(
        state.scope,
        state.requirements,
        state.estimation,
        state.risk
    )
    return state
