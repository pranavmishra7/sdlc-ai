import asyncio
from celery import shared_task
from app.workflows.sdlc_graph import run_sdlc_workflow
from app.storage.job_store import JobStore
from app.state.sdlc_state import SDLCState
from app.services.sse_manager import sse_manager


def _safe_emit(job_id: str, payload: dict):
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(sse_manager.publish(job_id, payload))
    except RuntimeError:
        pass


@shared_task(bind=True, autoretry_for=(), retry_kwargs={"max_retries": 0})
def run_sdlc_job(self, job_id: str):
    """
    Celery entrypoint.
    Receives ONLY job_id (string).
    """
    job_store = JobStore(job_id)

    # Load state from storage
    state_data = job_store.load_status()
    state = SDLCState.from_dict(state_data)

    _safe_emit(job_id, {
        "event": "job_started",
        "job_id": job_id,
    })

    # Run workflow
    state = run_sdlc_workflow(state)

    # Persist final state
    job_store.save_status(state.to_dict())

    _safe_emit(job_id, {
        "event": "job_finished",
        "job_id": job_id,
        "status": state.current_step,
    })

    return state.to_dict()
