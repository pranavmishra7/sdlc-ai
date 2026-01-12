from app.state.sdlc_state import SDLCState
from app.agents.requirements_agent import run_requirements


def requirements_node(state: SDLCState) -> SDLCState:
    step = "requirements"

    try:
        state.start_step(step)

        context = state.build_context()
        result = run_requirements(context)

        state.complete_step(
            step=step,
            raw_output=result["raw_output"],
        )

        return state

    except Exception as e:
        state.fail_step(step=step, error=e)
        return state
