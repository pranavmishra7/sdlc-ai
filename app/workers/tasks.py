import asyncio
from celery import shared_task
from app.workflows.sdlc_graph import run_sdlc_workflow
from app.storage.job_store import JobStore
from app.services.sse_manager import sse_manager


def _safe_emit(job_id: str, payload: dict):
    """
    Celery-safe SSE emitter.
    """
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(sse_manager.publish(job_id, payload))
    except RuntimeError:
        # No event loop in Celery → ignore
        pass


@shared_task(bind=True, autoretry_for=(), retry_kwargs={"max_retries": 0})
def run_sdlc_job(self, state_dict: dict):
    job_id = state_dict["job_id"]
    job_store = JobStore(job_id)

    # Emit job started (SAFE)
    _safe_emit(
        job_id,
        {
            "event": "job_started",
            "job_id": job_id,
        },
    )

    # Run workflow
    state = run_sdlc_workflow(state_dict)

    # Persist final state
    job_store.save_status(state.to_dict())

    # Emit job finished (SAFE)
    _safe_emit(
        job_id,
        {
            "event": "job_finished",
            "job_id": job_id,
            "status": state.current_step,
        },
    )

    return state.to_dict()
