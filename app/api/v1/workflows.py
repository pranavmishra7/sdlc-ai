import asyncio
import json
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse

from app.state.sdlc_state import SDLCState
from app.storage.job_store import JobStore
from app.workers.tasks import run_sdlc_job
from app.services.sse_manager import sse_manager

router = APIRouter(prefix="/workflows", tags=["workflows"])


# -------------------------------------------------
# Start / Resume
# -------------------------------------------------
@router.post("/start")
def start_or_resume(payload: dict):
    product_idea = payload.get("product_idea")
    job_id = payload.get("job_id")

    if job_id:
        if JobStore(job_id).load_status() is None:
            raise HTTPException(404, "Job not found")
        run_sdlc_job.delay(job_id)
        return {"job_id": job_id, "message": "Workflow resumed"}

    if not product_idea:
        raise HTTPException(400, "product_idea is required")

    job_id = str(uuid4())
    state = SDLCState(job_id, product_idea)
    JobStore(job_id).save_status(state.to_dict())
    run_sdlc_job.delay(job_id)

    return {"job_id": job_id, "message": "Workflow started"}


# -------------------------------------------------
# Job Status (UI uses this)
# -------------------------------------------------
@router.get("/{job_id}/status")
def get_job_status(job_id: str):
    store = JobStore(job_id)
    status = store.load_status()
    if status is None:
        raise HTTPException(404, "Job not found")
    return status


# -------------------------------------------------
# Admin: List Dead-letter Jobs
# -------------------------------------------------
@router.get("/admin/dead-letter")
def list_dead_letter_jobs():
    return JobStore.list_dead_letter_jobs()


# -------------------------------------------------
# Admin: Inspect Job
# -------------------------------------------------
@router.get("/admin/jobs/{job_id}")
def inspect_job(job_id: str):
    store = JobStore(job_id)
    status = store.load_status()
    if status is None:
        raise HTTPException(404, "Job not found")
    return status


# -------------------------------------------------
# Admin: Reset Dead-letter Job
# -------------------------------------------------
@router.post("/admin/jobs/{job_id}/reset")
def reset_dead_letter_job(job_id: str):
    store = JobStore(job_id)
    status = store.load_status()
    if status is None:
        raise HTTPException(404, "Job not found")

    state = SDLCState.from_dict(status)

    if not state.is_dead_lettered():
        raise HTTPException(400, "Job is not dead-lettered")

    failed_step = state.dead_letter["step"]

    state.dead_letter = None
    state.steps[failed_step] = "pending"
    state.errors.pop(failed_step, None)
    state.retries[failed_step] = 0
    state.current_step = failed_step

    store.save_status(state.to_dict())

    asyncio.create_task(
        sse_manager.publish(
            job_id,
            {"event": "job_reset", "step": failed_step},
        )
    )

    run_sdlc_job.delay(job_id)

    return {"job_id": job_id, "message": "Job reset and resumed"}


# -------------------------------------------------
# SSE Events
# -------------------------------------------------
@router.get("/events/{job_id}")
async def stream_events(job_id: str, request: Request):
    if JobStore(job_id).load_status() is None:
        raise HTTPException(404, "Job not found")

    queue = sse_manager.register(job_id)

    async def generator():
        try:
            while True:
                if await request.is_disconnected():
                    break
                event = await queue.get()
                yield f"data: {json.dumps(event)}\n\n"
        finally:
            sse_manager.unregister(job_id, queue)

    return StreamingResponse(generator(), media_type="text/event-stream")


@router.get("/{job_id}/steps/{step}")
def get_step(job_id: str, step: str):
    store = JobStore(job_id)
    status = store.load_status()
    if status is None:
        raise HTTPException(404, "Job not found")

    if step not in status["steps"]:
        raise HTTPException(404, "Step not found")

    step_data = store.load_step(step)

    return {
        "step": step,
        "status": status["steps"][step],
        "data": step_data,
        "error": status["errors"].get(step),
    }
