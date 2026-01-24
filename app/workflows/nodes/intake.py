from app.state.sdlc_state import SDLCState
from app.agents.intake_agent import run_intake
from app.quality.gate import run_quality_gate


def intake_node(state: SDLCState) -> SDLCState:
    step = "intake"

    try:
        state.start_step(step)

        result = run_intake(state.product_idea)
        # run_quality_gate(step=step, raw_output=result["raw_output"])
        state.complete_step(
            step=step, raw_output=result["raw_output"], parsed_output=result["content"]
        )

        return state

    except Exception as e:
        state.fail_step(step=step, error=e)
        return state
