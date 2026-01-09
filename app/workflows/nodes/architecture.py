import asyncio
from app.state.sdlc_state import SDLCState
from app.agents.architecture_agent import run_architecture
from app.storage.job_store import JobStore
from app.services.sse_manager import sse_manager


def architecture_node(state: SDLCState) -> SDLCState:
    job_store = JobStore(state.job_id)

    try:
        state.mark_step_running("architecture")
        job_store.save_status(state.to_dict())

        result = run_architecture({
            "intake": state.intake,
            "scope": state.scope,
            "requirements": state.requirements,
        })

        job_store.save_step("architecture", result)

        state.architecture = result
        state.mark_step_completed("architecture")
        state.set_current_step("estimation")
        job_store.save_status(state.to_dict())

        asyncio.create_task(
            sse_manager.publish(
                state.job_id,
                {
                    "event": "step_completed",
                    "step": "architecture",
                    "data": result,
                },
            )
        )

        return state

    except Exception as exc:
        state.mark_step_failed("architecture", exc, retryable=True)
        job_store.save_status(state.to_dict())

        asyncio.create_task(
            sse_manager.publish(
                state.job_id,
                {
                    "event": "step_failed",
                    "step": "architecture",
                    "error": state.errors.get("architecture"),
                },
            )
        )

        return state
