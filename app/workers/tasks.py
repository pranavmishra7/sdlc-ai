# app/workers/tasks.py

import asyncio
from celery import shared_task
from sqlalchemy.exc import OperationalError

from app.workflows.sdlc_graph import run_sdlc_workflow
from app.storage.job_store import JobStore
from app.state.sdlc_state import SDLCState, SDLCJobStatus
from app.services.sse_manager import sse_manager

# DB / RLS imports
from app.db.session import SessionLocal
from app.db.rls import set_tenant_context


def _safe_emit(job_id: str, payload: dict):
    """
    Fire-and-forget SSE.
    Must NEVER crash Celery worker.
    """
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(sse_manager.publish(job_id, payload))
    except RuntimeError:
        # No event loop (normal in Celery workers)
        pass
    except Exception:
        # SSE is best-effort only
        pass


def _safe_close_db(db):
    """
    Safely close SQLAlchemy session.
    Handles Postgres SSL disconnects gracefully.
    """
    if not db:
        return

    try:
        db.close()
    except OperationalError:
        # SSL connection already closed by Postgres
        # Safe to ignore
        pass
    except Exception:
        # Never allow cleanup to crash worker
        pass


@shared_task(bind=True, autoretry_for=(), retry_kwargs={"max_retries": 0})
def run_sdlc_job(self, job_id: str, tenant_id: str):
    """
    Celery entrypoint.

    - Executes EXACTLY ONE SDLC step per invocation
    - Re-enqueues itself until workflow completes
    - DB session MUST NOT survive long LLM calls
    """

    if not tenant_id:
        raise RuntimeError("tenant_id is required for run_sdlc_job")

    db = SessionLocal()
    try:
        # 🔐 Apply tenant RLS context
        set_tenant_context(db, tenant_id)

        store = JobStore(job_id)
        state_data = store.load_status()

        if state_data is None:
            return

        state = SDLCState.from_dict(state_data)

        _safe_emit(job_id, {
            "event": "step_started",
            "step": state.current_step
        })

        try:
            state = run_sdlc_workflow(state)
        except Exception as exc:
            state.fail_step(state.current_step, exc)
        finally:
            store.save_status(state.to_dict())

        _safe_emit(job_id, {
            "event": "step_finished",
            "step": state.current_step
        })

        # 🔁 Re-enqueue if workflow still running
        if (
            state.current_step not in ("completed", "dead_letter")
            and state.job_status != SDLCJobStatus.WAITING_APPROVAL
        ):
            self.apply_async(
                args=(job_id,),
                kwargs={"tenant_id": tenant_id},
            )

        return state.to_dict()

    finally:
        _safe_close_db(db)


@shared_task(bind=True, autoretry_for=(), retry_kwargs={"max_retries": 0})
def resume_sdlc_job(self, job_id: str, tenant_id: str):
    """
    Resume workflow after approval.

    - Idempotent
    - Safe to retry
    - Does NOT assume active DB connection
    """

    if not tenant_id:
        raise RuntimeError("tenant_id is required for resume_sdlc_job")

    db = SessionLocal()
    try:
        # 🔐 Apply tenant RLS context
        set_tenant_context(db, tenant_id)

        store = JobStore(job_id)
        state_data = store.load_status()

        if not state_data:
            return

        state = SDLCState.from_dict(state_data)

        # 🛑 Idempotency guard
        if state.job_status != SDLCJobStatus.WAITING_APPROVAL:
            return

        # ▶ Resume workflow
        state.job_status = SDLCJobStatus.RUNNING
        store.save_status(state.to_dict())

        # Continue execution asynchronously
        self.apply_async(
            args=(job_id,),
            kwargs={"tenant_id": tenant_id},
        )

    finally:
        _safe_close_db(db)
