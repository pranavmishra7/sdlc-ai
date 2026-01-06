from app.state.sdlc_state import SDLCState
from app.agents.risk_agent import run_risk

def risk_node(state: SDLCState) -> SDLCState:
    state.risk = run_risk(
        state.requirements,
        state.architecture
    )
    return state
