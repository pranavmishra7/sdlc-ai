from app.state.sdlc_state import SDLCState
from app.agents.scope_agent import run_scope


def scope_node(state: SDLCState) -> SDLCState:
    step = "scope"

    try:
        state.start_step(step)

        context = state.build_context()
        result = run_scope(context)

        state.complete_step(
            step=step,
            raw_output=result["raw_output"],
        )

        return state

    except Exception as e:
        state.fail_step(step=step, error=e)
        return state
