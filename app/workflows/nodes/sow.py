import asyncio
from app.state.sdlc_state import SDLCState
from app.agents.sow_agent import run_sow
from app.storage.job_store import JobStore
from app.services.sse_manager import sse_manager


def sow_node(state: SDLCState) -> SDLCState:
    job_store = JobStore(state.job_id)

    try:
        state.mark_step_running("sow")
        job_store.save_status(state.to_dict())

        result = run_sow({
            "intake": state.intake,
            "scope": state.scope,
            "requirements": state.requirements,
            "architecture": state.architecture,
            "estimation": state.estimation,
            "risk": state.risk,
        })

        job_store.save_step("sow", result)

        state.sow = result
        state.mark_step_completed("sow")
        state.set_current_step("completed")
        job_store.save_status(state.to_dict())

        asyncio.create_task(
            sse_manager.publish(
                state.job_id,
                {
                    "event": "step_completed",
                    "step": "sow",
                    "data": result,
                },
            )
        )

        return state

    except Exception as exc:
        state.mark_step_failed("sow", exc, retryable=False)
        job_store.save_status(state.to_dict())

        asyncio.create_task(
            sse_manager.publish(
                state.job_id,
                {
                    "event": "step_failed",
                    "step": "sow",
                    "error": state.errors.get("sow"),
                },
            )
        )

        return state
