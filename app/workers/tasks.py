from celery import shared_task
from time import sleep
import asyncio

from app.state.sdlc_state import SDLCState
from app.storage.job_store import JobStore
from app.workflows.sdlc_graph import run_sdlc_workflow
from app.services.sse_manager import sse_manager


@shared_task(bind=True)
def run_sdlc_job(self, job_id: str):
    """
    Run or resume SDLC workflow with per-step retry policies.
    """

    job_store = JobStore(job_id)
    status = job_store.load_status()

    if status is None:
        raise RuntimeError(f"Job {job_id} not found")

    state = SDLCState.from_dict(status)

    # Do not run dead-lettered jobs
    if state.is_dead_lettered():
        return {"job_id": job_id, "status": "dead_letter"}

    # Run workflow
    state = run_sdlc_workflow(state)
    job_store.save_status(state.to_dict())

    failed_step = state.failed_step()
    if not failed_step:
        return {"job_id": job_id, "status": "completed"}

    # -------------------------
    # Auto-retry with policy
    # -------------------------
    if state.can_auto_retry(failed_step):
        state.increment_retry(failed_step)
        state.steps[failed_step] = "pending"
        job_store.save_status(state.to_dict())

        asyncio.create_task(
            sse_manager.publish(
                job_id,
                {
                    "event": "step_auto_retry",
                    "step": failed_step,
                    "attempt": state.retries[failed_step],
                    "max_attempts": state.max_retries_for(failed_step),
                },
            )
        )

        # Linear backoff per attempt
        sleep(5 * state.retries[failed_step])

        return run_sdlc_job.delay(job_id)

    # -------------------------
    # Dead-letter
    # -------------------------
    state.mark_dead_letter(failed_step)
    job_store.save_status(state.to_dict())

    asyncio.create_task(
        sse_manager.publish(
            job_id,
            {
                "event": "job_dead_lettered",
                "step": failed_step,
                "error": state.dead_letter["error"],
            },
        )
    )

    return {
        "job_id": job_id,
        "status": "dead_letter",
        "failed_step": failed_step,
    }
