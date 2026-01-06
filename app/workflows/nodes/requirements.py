from app.state.sdlc_state import SDLCState
from app.agents.requirements_agent import run_requirements

def requirements_node(state: SDLCState) -> SDLCState:
    state.requirements = run_requirements(state.scope)
    return state
