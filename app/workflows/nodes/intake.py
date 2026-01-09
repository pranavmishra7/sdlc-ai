import asyncio
from app.state.sdlc_state import SDLCState
from app.agents.intake_agent import run_intake
from app.storage.job_store import JobStore
from app.services.sse_manager import sse_manager


def _safe_emit(job_id: str, payload: dict):
    """
    Safely emit SSE event from sync context (Celery-safe).
    """
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(sse_manager.publish(job_id, payload))
    except RuntimeError:
        # No running loop → ignore SSE instead of crashing worker
        pass


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
        state.current_step = "scope"   # ✅ FIX
        job_store.save_status(state.to_dict())

        # Emit success SSE event
        _safe_emit(
            state.job_id,
            {
                "event": "step_completed",
                "step": "intake",
                "data": result,
            },
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
        _safe_emit(
            state.job_id,
            {
                "event": "step_failed",
                "step": "intake",
                "error": state.errors.get("intake"),
            },
        )

        # Stop workflow progression
        return state
