import asyncio

from app.workers.celery_worker import celery_app
from app.workflows.sdlc_graph import run_sdlc_workflow
from app.storage.job_store import JobStore
from app.state.sdlc_state import SDLCState
from app.services.sse_manager import sse_manager


def _safe_emit(job_id: str, payload: dict):
    """
    Emit SSE event if an event loop exists.
    Celery workers usually don't have one.
    """
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(sse_manager.publish(job_id, payload))
    except RuntimeError:
        pass


@celery_app.task(
    name="app.workers.tasks.run_sdlc_job",
    bind=True,
    autoretry_for=(),
    retry_kwargs={"max_retries": 0},
)
def run_sdlc_job(self, job_id: str):
    """
    Executes EXACTLY ONE SDLC step.
    Re-enqueues itself until workflow is completed or dead-lettered.
    """

    store = JobStore(job_id)
    state_data = store.load_status()
    if state_data is None:
        return

    state = SDLCState.from_dict(state_data)

    _safe_emit(job_id, {
        "event": "job_step_started",
        "job_id": job_id,
        "step": state.current_step,
    })

    try:
        state = run_sdlc_workflow(state)

    except Exception as e:
        # Never crash Celery
        state.mark_step_failed(step=state.current_step, error=str(e))
        store.save_status(state.to_dict())
        return state.to_dict()

    store.save_status(state.to_dict())

    _safe_emit(job_id, {
        "event": "job_step_finished",
        "job_id": job_id,
        "step": state.current_step,
    })

    # Re-enqueue next step if workflow is not finished
    if state.current_step not in ("completed", "dead_letter"):
        celery_app.send_task(
            "app.workers.tasks.run_sdlc_job",
            args=[job_id],
        )

    return state.to_dict()
