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

        # retry policy (tunable)
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
        self.current_step = step
        return self

    def complete_step(
        self,
        step: str,
        raw_output: Optional[str] = None,
        parsed_output: Optional[dict] = None,
        output_type: Optional[str] = None,
    ):
        self.steps[step] = "completed"
        self.step_completed_at[step] = datetime.utcnow().isoformat()

        self.outputs[step] = {
            "type": output_type,
            "raw": raw_output,
            "parsed": parsed_output,
        }

        self._advance_step(step)
        return self

    def fail_step(self, step: str, error: Exception):
        """
        Mark a step as failed and dead-letter the workflow if retries are exhausted.
        """

        error_payload = {
            "message": str(error),
            "type": error.__class__.__name__,
        }

        self.steps[step] = "failed"
        self.errors[step] = error_payload
        self.step_completed_at[step] = datetime.utcnow().isoformat()

        self.retries[step] = self.retries.get(step, 0) + 1

        # retry if allowed
        if self.retries[step] <= self.retry_policy.get(step, 0):
            self.steps[step] = "pending"
            self.current_step = step
            return self

        # dead-letter
        self.current_step = "dead_letter"
        self.dead_letter = {
            "step": step,
            "error": error_payload,
            "failed_at": datetime.utcnow().isoformat(),
        }
        return self

    def is_completed(self) -> bool:
        return all(v == "completed" for v in self.steps.values())

    def _advance_step(self, completed_step: str):
        order = list(self.steps.keys())
        idx = order.index(completed_step)

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
        state.steps = data.get("steps", state.steps)
        state.current_step = data.get("current_step", "intake")
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

        for step in self.steps:
            out = self.outputs.get(step)
            if out and out.get("raw"):
                parts.append(out["raw"])

        return "\n\n".join(parts)

    def build_context(self) -> str:
        """
        Backward-compatible alias used by workflow nodes.
        """
        return self.get_context()
