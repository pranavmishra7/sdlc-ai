import asyncio
from app.state.sdlc_state import SDLCState
from app.agents.requirements_agent import run_requirements
from app.storage.job_store import JobStore
from app.services.sse_manager import sse_manager


def requirements_node(state: SDLCState) -> SDLCState:
    job_store = JobStore(state.job_id)

    try:
        state.mark_step_running("requirements")
        job_store.save_status(state.to_dict())

        result = run_requirements({
            "intake": state.intake,
            "scope": state.scope
        })

        job_store.save_step("requirements", result)

        state.requirements = result
        state.mark_step_completed("requirements")
        state.set_current_step("architecture")
        job_store.save_status(state.to_dict())

        asyncio.create_task(
            sse_manager.publish(
                state.job_id,
                {
                    "event": "step_completed",
                    "step": "requirements",
                    "data": result,
                },
            )
        )

        return state

    except Exception as exc:
        state.mark_step_failed("requirements", exc, retryable=True)
        job_store.save_status(state.to_dict())

        asyncio.create_task(
            sse_manager.publish(
                state.job_id,
                {
                    "event": "step_failed",
                    "step": "requirements",
                    "error": state.errors.get("requirements"),
                },
            )
        )

        return state
