from app.state.sdlc_state import SDLCState
from app.agents.sow_agent import run_sow

def sow_node(state: SDLCState):
    sow_output = run_sow(
        scope=state.scope,              
        requirements=state.requirements,
        estimation=state.estimation,
        risks=state.risk,
    )
    print("SOW TYPE:", type(sow_output))
    state.sow = sow_output
    return state

