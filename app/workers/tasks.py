import asyncio
from celery import shared_task

from app.workflows.sdlc_graph import run_sdlc_workflow
from app.storage.job_store import JobStore
from app.state.sdlc_state import SDLCState
from app.services.sse_manager import sse_manager


def _safe_emit(job_id: str, payload: dict):
    """
    Fire-and-forget SSE.
    Never allowed to crash the worker.
    """
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(sse_manager.publish(job_id, payload))
    except RuntimeError:
        # No event loop (normal in Celery)
        pass
    except Exception:
        # Absolutely nothing propagates
        pass


@shared_task(bind=True, autoretry_for=(), retry_kwargs={"max_retries": 0})
def run_sdlc_job(self, job_id: str):
    """
    Celery entrypoint.

    Executes EXACTLY ONE SDLC step.
    Re-enqueues itself until:
    - workflow is completed
    - or dead-lettered
    """

    store = JobStore(job_id)
    state_data = store.load_status()

    # Defensive: job deleted or corrupted
    if state_data is None:
        return

    state = SDLCState.from_dict(state_data)

    _safe_emit(job_id, {
        "event": "step_started",
        "step": state.current_step,
    })

    try:
        # Run ONE step (graph handles exceptions)
        state = run_sdlc_workflow(state)

    except Exception as exc:
        # Absolute last-resort catch (should never happen)
        state.fail_step(state.current_step, exc)

    finally:
        # 🔒 ALWAYS persist
        store.save_status(state.to_dict())

    _safe_emit(job_id, {
        "event": "step_finished",
        "step": state.current_step,
    })

    # 🔁 Re-enqueue only if needed
    if state.current_step not in ("completed", "dead_letter"):
        run_sdlc_job.delay(job_id)

    return state.to_dict()
