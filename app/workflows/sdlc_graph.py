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
    FINAL state-driven SDLC workflow runner.

    Guarantees:
    - Executes ONLY ONE step per invocation
    - Never re-runs completed steps
    - Correctly marks running/completed
    - Safe for retries & resume
    """

    job_store = JobStore(state.job_id)

    # -------------------------------------------------
    # Load persisted state (resume-safe)
    # -------------------------------------------------
    persisted = job_store.load_status()
    if persisted:
        state.current_step = persisted.get("current_step", state.current_step)
        state.steps = persisted.get("steps", state.steps)
        state.errors = persisted.get("errors", {})
        state.retries = persisted.get("retries", state.retries)
        state.dead_letter = persisted.get("dead_letter")

        # Restore completed outputs
        for step in SDLC_ORDER:
            if state.steps.get(step) == "completed":
                setattr(state, step, job_store.load_step(step))

    # -------------------------------------------------
    # Stop conditions
    # -------------------------------------------------
    if state.current_step in ("completed", "dead_letter"):
        return state

    step = state.current_step

    if step not in SDLC_NODES:
        raise RuntimeError(f"Invalid current_step: {step}")

    # -------------------------------------------------
    # Skip already-completed step (advance pointer only)
    # -------------------------------------------------
    if state.steps.get(step) == "completed":
        idx = SDLC_ORDER.index(step) + 1
        if idx >= len(SDLC_ORDER):
            state.current_step = "completed"
        else:
            state.current_step = SDLC_ORDER[idx]

        job_store.save_status(state.to_dict())
        return state

    # -------------------------------------------------
    # Execute EXACTLY ONE step
    # -------------------------------------------------
    node = SDLC_NODES[step]

    state = node(state)

    # -------------------------------------------------
    # Persist after node execution
    # -------------------------------------------------
    job_store.save_status(state.to_dict())

    return state
