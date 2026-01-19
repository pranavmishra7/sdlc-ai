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

# 🔒 Steps requiring approval
APPROVAL_STEPS = {"architecture", "estimation"}


def run_sdlc_workflow(state: SDLCState) -> SDLCState:
    if state.current_step in ("completed", "dead_letter"):
        return state

    step = state.current_step
    node = NODE_MAP.get(step)

    if not node:
        raise RuntimeError(f"No node registered for step '{step}'")

    state.start_step(step)

    try:
        state = node(state)

        if step in APPROVAL_STEPS:
            state.step_approvals[step] = ApprovalStatus.PENDING
            state.job_status = SDLCJobStatus.WAITING_APPROVAL
            return state

        return state

    except Exception as exc:
        state.fail_step(step, exc)
        return state
