from datetime import datetime
from typing import Dict, Any, Optional


class SDLCState:
    def __init__(self, job_id: str, product_idea: str):
        self.job_id = job_id
        self.product_idea = product_idea

        self.steps = {
            "intake": "pending",
            "scope": "pending",
            "requirements": "pending",
            "architecture": "pending",
            "estimation": "pending",
            "risk": "pending",
            "sow": "pending",
        }

        self.current_step = "intake"

        self.outputs: Dict[str, Dict[str, Any]] = {}
        self.errors: Dict[str, Any] = {}
        self.retries: Dict[str, int] = {}
        self.step_started_at: Dict[str, str] = {}
        self.step_completed_at: Dict[str, str] = {}

        self.dead_letter: Optional[Dict[str, Any]] = None

        # retry policy (can be tuned later)
        self.retry_policy = {
            "intake": 0,
            "scope": 0,
            "requirements": 1,
            "architecture": 1,
            "estimation": 0,
            "risk": 0,
            "sow": 0,
        }

    # ----------------------------
    # Lifecycle helpers
    # ----------------------------

    def start_step(self, step: str):
        self.steps[step] = "running"
        self.step_started_at[step] = datetime.utcnow().isoformat()

    def complete_step(self, step: str, output: dict):
        self.steps[step] = "completed"
        self.step_completed_at[step] = datetime.utcnow().isoformat()

        self.outputs[step] = {
            "type": output.get("type"),
            "raw": output.get("raw"),
            "parsed": output.get("parsed"),
        }

        self._advance_step()
        return self


    def fail_step(self, step: str, exc: Exception):
        retries = self.retries.get(step, 0) + 1
        self.retries[step] = retries

        self.errors[step] = {
            "message": str(exc),
            "type": type(exc).__name__,
        }

        max_retries = self.retry_policy.get(step, 0)

        if retries > max_retries:
            self.steps[step] = "failed"
            self.dead_letter = {
                "step": step,
                "error": self.errors[step],
                "failed_at": datetime.utcnow().isoformat(),
            }
            self.current_step = "dead_letter"
        else:
            # retry same step
            self.steps[step] = "pending"
            self.current_step = step

    def is_completed(self) -> bool:
        return all(v == "completed" for v in self.steps.values())

    def _advance_step(self):
        order = list(self.steps.keys())
        idx = order.index(self.current_step)

        if idx + 1 < len(order):
            self.current_step = order[idx + 1]
        else:
            self.current_step = "completed"

    # ----------------------------
    # Serialization
    # ----------------------------

    def to_dict(self) -> dict:
        return {
            "job_id": self.job_id,
            "product_idea": self.product_idea,
            "steps": self.steps,
            "current_step": self.current_step,
            "outputs": self.outputs,
            "errors": self.errors,
            "retries": self.retries,
            "retry_policy": self.retry_policy,
            "step_started_at": self.step_started_at,
            "step_completed_at": self.step_completed_at,
            "dead_letter": self.dead_letter,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "SDLCState":
        state = cls(data["job_id"], data["product_idea"])
        state.steps = data["steps"]
        state.current_step = data["current_step"]
        state.outputs = data.get("outputs", {})
        state.errors = data.get("errors", {})
        state.retries = data.get("retries", {})
        state.retry_policy = data.get("retry_policy", state.retry_policy)
        state.step_started_at = data.get("step_started_at", {})
        state.step_completed_at = data.get("step_completed_at", {})
        state.dead_letter = data.get("dead_letter")
        return state

    # ----------------------------
    # Context for agents
    # ----------------------------

    def get_context(self) -> str:
        """
        Build cumulative context for downstream agents.
        """
        parts = [self.product_idea]

        for step, out in self.outputs.items():
            raw = out.get("raw")
            if raw:
                parts.append(raw)

        return "\n\n".join(parts)
