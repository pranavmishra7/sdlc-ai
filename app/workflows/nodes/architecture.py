from app.state.sdlc_state import SDLCState
from app.agents.architecture_agent import run_architecture


def architecture_node(state: SDLCState) -> SDLCState:
    step = "architecture"

    try:
        state.start_step(step)

        context = state.build_context()
        result = run_architecture(context)

        state.complete_step(
            step=step,
            raw_output=result["raw_output"],
        )

        return state

    except Exception as e:
        state.fail_step(step=step, error=e)
        return state
