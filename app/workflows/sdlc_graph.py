from app.workflows.nodes.intake import intake_node
from app.workflows.nodes.scope import scope_node
from app.workflows.nodes.requirements import requirements_node
from app.workflows.nodes.architecture import architecture_node
from app.workflows.nodes.estimation import estimation_node
from app.workflows.nodes.risk import risk_node
from app.workflows.nodes.sow import sow_node
from app.storage.job_store import JobStore
from app.state.sdlc_state import SDLCState


SDLC_FLOW = [
    ("intake", intake_node),
    ("scope", scope_node),
    ("requirements", requirements_node),
    ("architecture", architecture_node),
    ("estimation", estimation_node),
    ("risk", risk_node),
    ("sow", sow_node),
]


def run_sdlc_workflow(state: SDLCState) -> SDLCState:
    """
    Run or resume SDLC workflow.
    Skips completed steps based on persisted state.
    """

    job_store = JobStore(state.job_id)
    persisted_status = job_store.load_status()

    # Resume support
    if persisted_status:
        state.current_step = persisted_status.get("current_step", state.current_step)
        state.steps.update(persisted_status.get("steps", {}))

        # Restore completed step outputs
        for step_name, _ in SDLC_FLOW:
            if state.steps.get(step_name) == "completed":
                setattr(state, step_name, job_store.load_step(step_name))

    for step_name, node in SDLC_FLOW:
        # Skip completed steps
        if state.steps.get(step_name) == "completed":
            continue

        # Mark running
        state.mark_step_running(step_name)
        job_store.save_status(state.to_dict())

        # Execute node
        state = node(state)

        # Persist after each step
        job_store.save_status(state.to_dict())

    return state
