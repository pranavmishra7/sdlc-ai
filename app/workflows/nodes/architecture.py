from app.state.sdlc_state import SDLCState
from app.agents.architecture_agent import run_architecture

def architecture_node(state: SDLCState) -> SDLCState:
    state.architecture = run_architecture(state.requirements)
    return state
