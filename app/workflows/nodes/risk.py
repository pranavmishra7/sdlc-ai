import asyncio
from app.state.sdlc_state import SDLCState
from app.agents.risk_agent import run_risk
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


def risk_node(state: SDLCState) -> SDLCState:
    job_store = JobStore(state.job_id)

    try:
        # Mark running
        state.mark_step_running("risk")
        job_store.save_status(state.to_dict())

        # Execute agent
        result = run_risk({
            "intake": state.intake,
            "scope": state.scope,
            "requirements": state.requirements,
            "architecture": state.architecture,
            "estimation": state.estimation,
        })

        # Persist step output
        job_store.save_step("risk", result)

        # Update state
        state.risk = result
        state.mark_step_completed("risk")
        state.current_step = "sow"   # ✅ FIX
        job_store.save_status(state.to_dict())

        # Emit success SSE event
        _safe_emit(
            state.job_id,
            {
                "event": "step_completed",
                "step": "risk",
                "data": result,
            },
        )

        return state

    except Exception as exc:
        # Mark failure
        state.mark_step_failed(
            step="risk",
            error=exc,
            retryable=True,
        )
        job_store.save_status(state.to_dict())

        # Emit failure SSE event
        _safe_emit(
            state.job_id,
            {
                "event": "step_failed",
                "step": "risk",
                "error": state.errors.get("risk"),
            },
        )

        return state
