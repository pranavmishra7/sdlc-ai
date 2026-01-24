from app.state.sdlc_state import SDLCState
from app.agents.risk_agent import run_risk
from app.quality.gate import run_quality_gate


def risk_node(state: SDLCState) -> SDLCState:
    step = "risk"

    try:
        state.start_step(step)

        context = state.build_context()
        result = run_risk(context)

        # run_quality_gate(step=step, raw_output=result["raw_output"])

        state.complete_step(
            step=step, raw_output=result["raw_output"], parsed_output=result["content"]
        )
        return state

    except Exception as e:
        state.fail_step(step=step, error=e)
        return state
