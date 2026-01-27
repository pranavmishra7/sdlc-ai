from app.state.sdlc_state import SDLCState
from app.agents.document_synthesis_agent import run_document_synthesis


def document_synthesis_node(state: SDLCState) -> SDLCState:
    step = "client_document"

    try:
        state.start_step(step)

        context = {
            "intake": state.outputs["intake"]["content"],
            "scope": state.outputs["scope"]["content"],
            "requirements": state.outputs["requirements"]["content"],
            "architecture": state.outputs["architecture"]["content"],
            "estimation": state.outputs["estimation"]["content"],
            "risk": state.outputs["risk"]["content"],
            "sow": state.outputs["sow"]["content"],
        }

        result = run_document_synthesis(context)

        state.complete_step(
            step=step,
            raw_output=result["raw_output"],
            parsed_output=result["content"],  # publishing output
        )

        return state

    except Exception as e:
        state.fail_step(step=step, error=e)
        return state
