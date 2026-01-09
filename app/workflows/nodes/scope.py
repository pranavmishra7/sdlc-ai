import asyncio
from app.state.sdlc_state import SDLCState
from app.agents.scope_agent import run_scope
from app.storage.job_store import JobStore
from app.services.sse_manager import sse_manager


def scope_node(state: SDLCState) -> SDLCState:
    job_store = JobStore(state.job_id)

    try:
        state.mark_step_running("scope")
        job_store.save_status(state.to_dict())

        result = run_scope({
            "intake": state.intake
        })

        job_store.save_step("scope", result)

        state.scope = result
        state.mark_step_completed("scope")
        state.set_current_step("requirements")
        job_store.save_status(state.to_dict())

        asyncio.create_task(
            sse_manager.publish(
                state.job_id,
                {
                    "event": "step_completed",
                    "step": "scope",
                    "data": result,
                },
            )
        )

        return state

    except Exception as exc:
        state.mark_step_failed("scope", exc, retryable=True)
        job_store.save_status(state.to_dict())

        asyncio.create_task(
            sse_manager.publish(
                state.job_id,
                {
                    "event": "step_failed",
                    "step": "scope",
                    "error": state.errors.get("scope"),
                },
            )
        )

        return state
