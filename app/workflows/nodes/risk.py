import asyncio
from app.state.sdlc_state import SDLCState
from app.agents.risk_agent import run_risk
from app.storage.job_store import JobStore
from app.services.sse_manager import sse_manager


def risk_node(state: SDLCState) -> SDLCState:
    job_store = JobStore(state.job_id)

    try:
        state.mark_step_running("risk")
        job_store.save_status(state.to_dict())

        result = run_risk({
            "intake": state.intake,
            "scope": state.scope,
            "requirements": state.requirements,
            "architecture": state.architecture,
            "estimation": state.estimation,
        })

        job_store.save_step("risk", result)

        state.risk = result
        state.mark_step_completed("risk")
        state.set_current_step("sow")
        job_store.save_status(state.to_dict())

        asyncio.create_task(
            sse_manager.publish(
                state.job_id,
                {
                    "event": "step_completed",
                    "step": "risk",
                    "data": result,
                },
            )
        )

        return state

    except Exception as exc:
        state.mark_step_failed("risk", exc, retryable=True)
        job_store.save_status(state.to_dict())

        asyncio.create_task(
            sse_manager.publish(
                state.job_id,
                {
                    "event": "step_failed",
                    "step": "risk",
                    "error": state.errors.get("risk"),
                },
            )
        )

        return state
