# app/api/v1/workflows.py

import asyncio
import json
from uuid import uuid4
from datetime import datetime

from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import StreamingResponse

from app.state.sdlc_state import SDLCState, SDLCJobStatus
from app.storage.job_store import JobStore
from app.workers.celery_worker import celery_app
from app.services.sse_manager import sse_manager

from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models.sdlc_job import SDLCJob

from app.api.deps import get_current_user
from app.db.models.sdlc_step import ApprovalStatus


router = APIRouter(prefix="/workflows", tags=["workflows"])


# ------------------------------------------------------------------
# Start / Resume Workflow
# ------------------------------------------------------------------

@router.post("/start")
def start_or_resume(payload: dict, user: dict = Depends(get_current_user)):
    product_idea = payload.get("product_idea")
    job_id = payload.get("job_id")

    if job_id:
        if JobStore(job_id).load_status() is None:
            raise HTTPException(404, "Job not found")

        celery_app.send_task(
            "app.workers.tasks.run_sdlc_job",
            args=[job_id],
            kwargs={"tenant_id": user["tenant_id"]},
        )
        return {"job_id": job_id, "message": "Workflow resumed"}

    if not product_idea:
        raise HTTPException(400, "product_idea is required")

    job_id = str(uuid4())
    state = SDLCState(job_id, product_idea)
    JobStore(job_id).save_status(state.to_dict())

    celery_app.send_task(
        "app.workers.tasks.run_sdlc_job",
        args=[job_id],
        kwargs={"tenant_id": user["tenant_id"]},
    )

    return {"job_id": job_id, "message": "Workflow started"}


# ------------------------------------------------------------------
# Approval APIs (NEW)
# ------------------------------------------------------------------

@router.post("/steps/{job_id}/{step}/approve")
def approve_step(job_id: str, step: str, user: dict = Depends(get_current_user)):
    store = JobStore(job_id)
    data = store.load_status()
    if not data:
        raise HTTPException(404, "Job not found")

    state = SDLCState.from_dict(data)

    if state.job_status != SDLCJobStatus.WAITING_APPROVAL:
        raise HTTPException(400, "Workflow is not waiting for approval")

    if state.step_approvals.get(step) != ApprovalStatus.PENDING:
        raise HTTPException(400, "Step is not pending approval")

    state.step_approvals[step] = ApprovalStatus.APPROVED
    state.job_status = SDLCJobStatus.RUNNING
    store.save_status(state.to_dict())

    celery_app.send_task(
        "app.workers.tasks.resume_sdlc_job",
        args=[job_id],
        kwargs={"tenant_id": user["tenant_id"]},
    )

    return {"status": "approved", "step": step}


@router.post("/steps/{job_id}/{step}/reject")
def reject_step(job_id: str, step: str, user: dict = Depends(get_current_user)):
    store = JobStore(job_id)
    data = store.load_status()
    if not data:
        raise HTTPException(404, "Job not found")

    state = SDLCState.from_dict(data)

    if state.step_approvals.get(step) != ApprovalStatus.PENDING:
        raise HTTPException(400, "Step is not pending approval")

    state.step_approvals[step] = ApprovalStatus.REJECTED
    state.job_status = SDLCJobStatus.DEAD_LETTER
    store.save_status(state.to_dict())

    return {"status": "rejected", "step": step}

# ------------------------------------------------------------------
# Status / Inspection APIs (Unchanged)
# ------------------------------------------------------------------

@router.get("/{job_id}/status")
def get_job_status(job_id: str):
    store = JobStore(job_id)
    status = store.load_status()
    if status is None:
        raise HTTPException(404, "Job not found")
    return status


@router.get("/{job_id}/steps/{step}")
def get_step(job_id: str, step: str):
    store = JobStore(job_id)
    status = store.load_status()

    if status is None:
        raise HTTPException(404, "Job not found")

    if step not in status["steps"]:
        raise HTTPException(404, "Step not found")

    output = status.get("outputs", {}).get(step)

    return {
        "step": step,
        "status": status["steps"][step],
        "data": {
            "raw_output": output.get("raw") if output else None,
            "parsed_output": output.get("parsed") if output else None,
            "started_at": status.get("step_started_at", {}).get(step),
            "completed_at": status.get("step_completed_at", {}).get(step),
        },
        "error": status.get("errors", {}).get(step),
    }


@router.get("/admin/dead-letter")
def list_dead_letter_jobs():
    return JobStore.list_dead_letter_jobs()


@router.get("/admin/jobs/{job_id}")
def inspect_job(job_id: str):
    store = JobStore(job_id)
    status = store.load_status()
    if status is None:
        raise HTTPException(404, "Job not found")
    return status


@router.post("/admin/jobs/{job_id}/reset")
def reset_dead_letter_job(job_id: str, user: dict = Depends(get_current_user)):
    store = JobStore(job_id)
    status = store.load_status()
    if status is None:
        raise HTTPException(404, "Job not found")

    state = SDLCState.from_dict(status)

    if not state.dead_letter:
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

    celery_app.send_task(
        "app.workers.tasks.run_sdlc_job",
        args=[job_id],
        kwargs={"tenant_id": user["tenant_id"]},
    )

    return {"job_id": job_id, "message": "Job reset and resumed"}


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


@router.get("/jobs")
def list_jobs(db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    return db.query(SDLCJob).filter(SDLCJob.tenant_id == user["tenant_id"]).all()
