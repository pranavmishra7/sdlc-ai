import asyncio
from app.state.sdlc_state import SDLCState
from app.agents.intake_agent import run_intake
from app.storage.job_store import JobStore
from app.services.sse_manager import sse_manager


def intake_node(state: SDLCState) -> SDLCState:
    """
    Intake workflow node (failure-aware)
    - Executes intake agent
    - Persists result
    - Emits SSE events
    - Handles failures safely
    """

    job_store = JobStore(state.job_id)

    try:
        # Mark running
        state.mark_step_running("intake")
        job_store.save_status(state.to_dict())

        # Execute agent
        result = run_intake(state.product_idea)

        # Persist step output
        job_store.save_step("intake", result)

        # Update state
        state.intake = result
        state.mark_step_completed("intake")
        state.set_current_step("scope")
        job_store.save_status(state.to_dict())

        # Emit success SSE event
        asyncio.create_task(
            sse_manager.publish(
                state.job_id,
                {
                    "event": "step_completed",
                    "step": "intake",
                    "data": result,
                },
            )
        )

        return state

    except Exception as exc:
        # Mark failure
        state.mark_step_failed(
            step_name="intake",
            error=exc,
            retryable=True,
        )
        job_store.save_status(state.to_dict())

        # Emit failure SSE event
        asyncio.create_task(
            sse_manager.publish(
                state.job_id,
                {
                    "event": "step_failed",
                    "step": "intake",
                    "error": state.errors.get("intake"),
                },
            )
        )

        # Stop workflow progression
        return state
