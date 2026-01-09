from typing import Dict, Any, Optional
from datetime import datetime


class SDLCState:
    """
    SDLC workflow state with:
    - per-step retry policies
    - failure handling
    - dead-letter support
    """

    SDLC_STEPS = [
        "intake",
        "scope",
        "requirements",
        "architecture",
        "estimation",
        "risk",
        "sow",
    ]

    # -------------------------
    # Per-step retry policy
    # -------------------------
    RETRY_POLICY = {
        "intake": 3,
        "scope": 2,
        "requirements": 2,
        "architecture": 1,
        "estimation": 1,
        "risk": 1,
        "sow": 0,   # never auto-retry
    }

    def __init__(self, job_id: str, product_idea: str):
        self.job_id = job_id
        self.product_idea = product_idea

        # Step outputs
        self.intake = None
        self.scope = None
        self.requirements = None
        self.architecture = None
        self.estimation = None
        self.risk = None
        self.sow = None

        # Status
        self.current_step = "intake"
        self.steps = {step: "pending" for step in self.SDLC_STEPS}

        # Errors & retries
        self.errors: Dict[str, Dict[str, Any]] = {}
        self.retries: Dict[str, int] = {step: 0 for step in self.SDLC_STEPS}

        # Dead-letter
        self.dead_letter: Optional[Dict[str, Any]] = None

    # -------------------------
    # Step transitions
    # -------------------------

    def mark_step_running(self, step: str):
        self.steps[step] = "running"

    def mark_step_completed(self, step: str):
        self.steps[step] = "completed"
        self.errors.pop(step, None)
        self.retries[step] = 0

    def mark_step_failed(self, step: str, error: Exception, retryable: bool = True):
        self.steps[step] = "failed"
        self.errors[step] = {
            "type": type(error).__name__,
            "message": str(error),
            "retryable": retryable,
        }
        self.current_step = step

    # -------------------------
    # Retry logic
    # -------------------------

    def max_retries_for(self, step: str) -> int:
        return self.RETRY_POLICY.get(step, 0)

    def can_auto_retry(self, step: str) -> bool:
        if step not in self.errors:
            return False
        if not self.errors[step].get("retryable", True):
            return False
        return self.retries[step] < self.max_retries_for(step)

    def increment_retry(self, step: str):
        self.retries[step] += 1

    # -------------------------
    # Dead-letter
    # -------------------------

    def mark_dead_letter(self, step: str):
        self.dead_letter = {
            "step": step,
            "error": self.errors.get(step),
            "failed_at": datetime.utcnow().isoformat(),
        }
        self.current_step = "dead_letter"

    def is_dead_lettered(self) -> bool:
        return self.dead_letter is not None

    def failed_step(self) -> Optional[str]:
        for step, status in self.steps.items():
            if status == "failed":
                return step
        return None

    # -------------------------
    # Serialization
    # -------------------------

    def to_dict(self) -> Dict[str, Any]:
        return {
            "job_id": self.job_id,
            "product_idea": self.product_idea,
            "current_step": self.current_step,
            "steps": self.steps,
            "errors": self.errors,
            "retries": self.retries,
            "dead_letter": self.dead_letter,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SDLCState":
        state = cls(
            job_id=data["job_id"],
            product_idea=data.get("product_idea", ""),
        )
        state.current_step = data.get("current_step", "intake")
        state.steps = data.get("steps", state.steps)
        state.errors = data.get("errors", {})
        state.retries = data.get("retries", state.retries)
        state.dead_letter = data.get("dead_letter")
        return state
