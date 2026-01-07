from app.workers.celery_worker import celery_app
from app.workflows.sdlc_graph import build_graph
from app.state.sdlc_state import SDLCState
from app.storage.job_store import JobStore
from app.state.job_state import JobStatus

store = JobStore()
graph = build_graph()

STEPS = [
    "intake",
    "scope",
    "requirements",
    "architecture",
    "estimation",
    "risk",
    "sow",
]


# ✅ SAFE serializer (CRITICAL FIX)
def safe_state_dump(state: SDLCState) -> dict:
    """
    Convert SDLCState to plain dict without calling model_dump()
    on nested dicts or strings.
    """
    return {
        k: v for k, v in state.__dict__.items()
    }


@celery_app.task(bind=True)
def run_sdlc(self, job_id: str, product_idea: str):
    step = None
    try:
        # mark job running
        store.set_running(job_id)

        job = store.get(job_id)
        start_step = store.get_next_step(job_id)

        # initial state
        state = SDLCState(
            job_id=job_id,
            product_idea=product_idea
        )

        # restore partial state (resume support)
        if job and job.get("result"):
            state = SDLCState(**job["result"])

        steps = list(job["steps"].keys())
        start_index = steps.index(start_step) if start_step else 0

        for step in steps[start_index:]:
            store.start_step(job_id, step)

            # LangGraph executes from this node forward
            state = graph.invoke(state, start_at=step)

            store.complete_step(job_id, step)

        # ✅ FINAL SAFE SAVE (NO model_dump)
        store.complete(job_id, safe_state_dump(state))
# exception handling
    except Exception as e:
        # mark failed step correctly
        if step:
            store.fail_step(job_id, step, repr(e))
        else:
            store.fail(job_id, repr(e))
        raise
