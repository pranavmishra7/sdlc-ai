from app.state.sdlc_state import SDLCState
from app.agents.sow_agent import run_sow


def sow_node(state: SDLCState) -> SDLCState:
    step = "sow"

    try:
        state.start_step(step)

        context = state.build_context()
        result = run_sow(context)

        state.complete_step(
            step=step,
            raw_output=result["raw_output"],
        )

        return state

    except Exception as e:
        state.fail_step(step=step, error=e)
        return state
