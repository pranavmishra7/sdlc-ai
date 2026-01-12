from app.state.sdlc_state import SDLCState

from app.workflows.nodes.intake import intake_node
from app.workflows.nodes.scope import scope_node
from app.workflows.nodes.requirements import requirements_node
from app.workflows.nodes.architecture import architecture_node
from app.workflows.nodes.estimation import estimation_node
from app.workflows.nodes.risk import risk_node
from app.workflows.nodes.sow import sow_node


NODE_MAP = {
    "intake": intake_node,
    "scope": scope_node,
    "requirements": requirements_node,
    "architecture": architecture_node,
    "estimation": estimation_node,
    "risk": risk_node,
    "sow": sow_node,
}


def run_sdlc_workflow(state: SDLCState) -> SDLCState:
    """
    Executes EXACTLY ONE SDLC step.

    - No looping
    - No persistence
    - No retries here
    """

    # Terminal states
    if state.current_step in ("completed", "dead_letter"):
        return state

    step = state.current_step
    node = NODE_MAP.get(step)

    if not node:
        raise RuntimeError(f"No node registered for step '{step}'")

    # Mark step running (authoritative)
    state.start_step(step)

    try:
        # Node MUST return updated state
        state = node(state)
        return state

    except Exception as exc:
        # Centralized failure handling
        state.fail_step(step, exc)
        return state
