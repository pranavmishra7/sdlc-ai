# app/workers/tasks.py
import asyncio
from celery import shared_task

from app.workflows.sdlc_graph import run_sdlc_workflow
from app.storage.job_store import JobStore
from app.state.sdlc_state import SDLCState
from app.services.sse_manager import sse_manager

# DB/rls imports
from app.db.session import SessionLocal
from app.db.rls import set_tenant_context


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
        pass


@shared_task(bind=True, autoretry_for=(), retry_kwargs={"max_retries": 0})
def run_sdlc_job(self, job_id: str, tenant_id: str):
    """
    Celery entrypoint.

    - tenant_id MUST be provided by the enqueuer (FastAPI).
    - We set DB tenant context (SET LOCAL) scoped to this task's DB session/transaction.
    """
    if not tenant_id:
        raise RuntimeError("tenant_id is required for run_sdlc_job")

    db = SessionLocal()
    try:
        # scope tenant to THIS DB connection/transaction
        set_tenant_context(db, tenant_id)

        # NOTE: JobStore and other components may use Redis/filesystem, but any
        # DB calls below will obey RLS because we just set the tenant.
        store = JobStore(job_id)
        state_data = store.load_status()

        if state_data is None:
            return

        state = SDLCState.from_dict(state_data)

        _safe_emit(job_id, {"event": "step_started", "step": state.current_step})

        try:
            state = run_sdlc_workflow(state)
        except Exception as exc:
            state.fail_step(state.current_step, exc)
        finally:
            store.save_status(state.to_dict())

        _safe_emit(job_id, {"event": "step_finished", "step": state.current_step})

        # Re-enqueue if more work remains. Always pass tenant_id so RLS is preserved.
        if state.current_step not in ("completed", "dead_letter"):
            self.apply_async(args=(job_id,), kwargs={"tenant_id": tenant_id})

        return state.to_dict()
    finally:
        db.close()
