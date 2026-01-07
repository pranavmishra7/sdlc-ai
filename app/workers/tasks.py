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

@celery_app.task(bind=True)
def run_sdlc(self, job_id: str, product_idea: str):
    try:
        store.set_running(job_id)

        job = store.get(job_id)
        start_step = store.get_next_step(job_id)

        state = SDLCState(
            job_id=job_id,
            product_idea=product_idea
        )

        # restore partial state if exists
        if job and job["result"]:
            state = SDLCState(**job["result"])

        steps = list(job["steps"].keys())

        start_index = steps.index(start_step) if start_step else 0

        for step in steps[start_index:]:
            store.start_step(job_id, step)

            state = graph.invoke(state, start_at=step)

            store.complete_step(job_id, step)

        store.complete(job_id, state.model_dump(mode="json"))

    except Exception as e:
            store.fail_step(job_id, step, repr(e))
            raise

    try:
        store.set_running(job_id)

        state = SDLCState(
            job_id=job_id,
            product_idea=product_idea
        )

        for step in STEPS:
            store.start_step(job_id, step)

            # LangGraph executes until next node automatically
            state = graph.invoke(state, start_at=step)

            store.complete_step(job_id, step)

        store.complete(job_id, state.model_dump(mode="json"))

    except Exception as e:
            store.fail_step(job_id, step, repr(e))
            raise
