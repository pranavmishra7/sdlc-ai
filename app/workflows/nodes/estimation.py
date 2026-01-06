from app.state.sdlc_state import SDLCState
from app.agents.estimation_agent import run_estimation

def estimation_node(state: SDLCState) -> SDLCState:
    state.estimation = run_estimation(
        state.requirements,
        state.architecture
    )
    return state
