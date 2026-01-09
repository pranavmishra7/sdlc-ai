import asyncio
from app.state.sdlc_state import SDLCState
from app.agents.sow_agent import run_sow
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


def sow_node(state: SDLCState) -> SDLCState:
    job_store = JobStore(state.job_id)

    try:
        # Mark running
        state.mark_step_running("sow")
        job_store.save_status(state.to_dict())

        # Execute agent
        result = run_sow({
            "intake": state.intake,
            "scope": state.scope,
            "requirements": state.requirements,
            "architecture": state.architecture,
            "estimation": state.estimation,
            "risk": state.risk,
        })

        # Persist step output
        job_store.save_step("sow", result)

        # Update state
        state.sow = result
        state.mark_step_completed("sow")
        state.current_step = "completed"   # ✅ FIX
        job_store.save_status(state.to_dict())

        # Emit success SSE event
        _safe_emit(
            state.job_id,
            {
                "event": "step_completed",
                "step": "sow",
                "data": result,
            },
        )

        return state

    except Exception as exc:
        # Mark failure (no auto-retry for SOW)
        state.mark_step_failed(
            step="sow",
            error=exc,
            retryable=False,
        )
        job_store.save_status(state.to_dict())

        # Emit failure SSE event
        _safe_emit(
            state.job_id,
            {
                "event": "step_failed",
                "step": "sow",
                "error": state.errors.get("sow"),
            },
        )

        return state
