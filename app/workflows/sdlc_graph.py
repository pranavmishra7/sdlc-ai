from app.workflows.nodes.intake import intake_node
from app.workflows.nodes.scope import scope_node
from app.workflows.nodes.requirements import requirements_node
from app.workflows.nodes.architecture import architecture_node
from app.workflows.nodes.estimation import estimation_node
from app.workflows.nodes.risk import risk_node
from app.workflows.nodes.sow import sow_node
from app.storage.job_store import JobStore
from app.state.sdlc_state import SDLCState


SDLC_ORDER = [
    "intake",
    "scope",
    "requirements",
    "architecture",
    "estimation",
    "risk",
    "sow",
]

SDLC_NODES = {
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
    State-driven SDLC workflow runner.
    Executes ONLY the current step and advances forward.
    """

    job_store = JobStore(state.job_id)

    # Load persisted state (resume support)
    persisted = job_store.load_status()
    if persisted:
        state.current_step = persisted.get("current_step", state.current_step)
        state.steps.update(persisted.get("steps", {}))
        state.errors = persisted.get("errors", {})
        state.retries = persisted.get("retries", state.retries)
        state.dead_letter = persisted.get("dead_letter")

        # Restore completed step outputs
        for step in SDLC_ORDER:
            if state.steps.get(step) == "completed":
                setattr(state, step, job_store.load_step(step))

    # Stop conditions
    if state.current_step in ("completed", "dead_letter"):
        return state

    step = state.current_step

    # Safety: invalid step
    if step not in SDLC_NODES:
        raise RuntimeError(f"Invalid current_step: {step}")

    # Do not re-run completed steps
    if state.steps.get(step) == "completed":
        idx = SDLC_ORDER.index(step) + 1
        if idx >= len(SDLC_ORDER):
            state.current_step = "completed"
            job_store.save_status(state.to_dict())
            return state
        state.current_step = SDLC_ORDER[idx]
        job_store.save_status(state.to_dict())
        return state

    # Execute ONLY the current step
    node = SDLC_NODES[step]
    state = node(state)

    # Persist after execution
    job_store.save_status(state.to_dict())

    return state
