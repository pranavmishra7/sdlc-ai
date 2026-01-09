import asyncio
from app.state.sdlc_state import SDLCState
from app.agents.estimation_agent import run_estimation
from app.storage.job_store import JobStore
from app.services.sse_manager import sse_manager


def estimation_node(state: SDLCState) -> SDLCState:
    job_store = JobStore(state.job_id)

    try:
        state.mark_step_running("estimation")
        job_store.save_status(state.to_dict())

        result = run_estimation({
            "intake": state.intake,
            "scope": state.scope,
            "requirements": state.requirements,
            "architecture": state.architecture,
        })

        job_store.save_step("estimation", result)

        state.estimation = result
        state.mark_step_completed("estimation")
        state.set_current_step("risk")
        job_store.save_status(state.to_dict())

        asyncio.create_task(
            sse_manager.publish(
                state.job_id,
                {
                    "event": "step_completed",
                    "step": "estimation",
                    "data": result,
                },
            )
        )

        return state

    except Exception as exc:
        state.mark_step_failed("estimation", exc, retryable=True)
        job_store.save_status(state.to_dict())

        asyncio.create_task(
            sse_manager.publish(
                state.job_id,
                {
                    "event": "step_failed",
                    "step": "estimation",
                    "error": state.errors.get("estimation"),
                },
            )
        )

        return state
