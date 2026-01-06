from app.state.sdlc_state import SDLCState
from app.agents.scope_agent import run_scope

def scope_node(state: SDLCState) -> SDLCState:
    state.scope = run_scope(state.intake)
    return state
