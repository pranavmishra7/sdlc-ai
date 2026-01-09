import asyncio
from app.state.sdlc_state import SDLCState
from app.agents.estimation_agent import run_estimation
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
        # No running event loop (Celery worker)
        pass


def estimation_node(state: SDLCState) -> SDLCState:
    job_store = JobStore(state.job_id)

    try:
        # Mark running
        state.mark_step_running("estimation")
        job_store.save_status(state.to_dict())

        # Execute agent
        result = run_estimation({
            "intake": state.intake,
            "scope": state.scope,
            "requirements": state.requirements,
            "architecture": state.architecture,
        })

        # Persist step output
        job_store.save_step("estimation", result)

        # Update state
        state.estimation = result
        state.mark_step_completed("estimation")
        state.current_step = "risk"   # ✅ FIX
        job_store.save_status(state.to_dict())

        # Emit success SSE event
        _safe_emit(
            state.job_id,
            {
                "event": "step_completed",
                "step": "estimation",
                "data": result,
            },
        )

        return state

    except Exception as exc:
        # Mark failure
        state.mark_step_failed(
            step="estimation",
            error=exc,
            retryable=True,
        )
        job_store.save_status(state.to_dict())

        # Emit failure SSE event
        _safe_emit(
            state.job_id,
            {
                "event": "step_failed",
                "step": "estimation",
                "error": state.errors.get("estimation"),
            },
        )

        return state
