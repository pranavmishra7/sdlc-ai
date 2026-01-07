import uuid
from fastapi import APIRouter, HTTPException
from app.workers.tasks import run_sdlc
from app.storage.job_store import JobStore

router = APIRouter()
store = JobStore()

@router.post("/start")
def start_workflow(product_idea: str):
    job_id = str(uuid.uuid4())

    store.create(job_id)

    run_sdlc.delay(job_id, product_idea)

    return {
        "job_id": job_id,
        "status": "queued"
    }

@router.get("/status/{job_id}")
def get_status(job_id: str):
    job = store.get(job_id)
    if not job:
        raise HTTPException(404, "Job not found")

    return {
        "job_id": job_id,
        "status": job["status"],
        "current_step": job["current_step"],
        "steps": job["steps"],
        "error": job.get("error"),
    }

@router.get("/result/{job_id}")
def get_result(job_id: str):
    job = store.get(job_id)
    if not job:
        raise HTTPException(404, "Job not found")

    if job["status"] != "completed":
        return {
            "status": job["status"]
        }

    return job["result"]

@router.post("/resume/{job_id}")
def resume_job(job_id: str):
    job = store.get(job_id)
    if not job:
        raise HTTPException(404, "Job not found")

    if job["status"] == "completed":
        return {"message": "Job already completed"}

    if not job["result"]:
        raise HTTPException(400, "No previous state to resume from")

    run_sdlc.delay(job_id, job["result"]["product_idea"])

    return {
        "job_id": job_id,
        "status": "resumed"
    }
