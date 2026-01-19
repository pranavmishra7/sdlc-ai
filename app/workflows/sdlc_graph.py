# app/workflows/sdlc_graph.py

from app.state.sdlc_state import SDLCState, SDLCJobStatus
from app.db.models.sdlc_step import ApprovalStatus

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
    - MAY PAUSE for approval
    """

    # Terminal states
    if state.current_step in ("completed", "dead_letter"):
        return state

    step = state.current_step
    node = NODE_MAP.get(step)

    if not node:
        raise RuntimeError(f"No node registered for step '{step}'")

    # Mark step running
    state.start_step(step)

    try:
        # Node returns updated state
        state = node(state)

        # 🔒 APPROVAL PAUSE LOGIC
        step_state = state.steps.get(step)

        if step_state and step_state.requires_approval:
            step_state.approval_status = ApprovalStatus.PENDING
            state.job_status = SDLCJobStatus.WAITING_APPROVAL
            return state  # ⛔ HARD PAUSE

        return state

    except Exception as exc:
        state.fail_step(step, exc)
        return state
