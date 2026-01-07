import json
import redis
from app.config.settings import settings
from app.state.job_state import JobStatus

STEPS = [
    "intake",
    "scope",
    "requirements",
    "architecture",
    "estimation",
    "risk",
    "sow",
]

class JobStore:
    def __init__(self):
        self.client = redis.Redis.from_url(
            settings.REDIS_URL,
            decode_responses=True
        )

    def _key(self, job_id: str) -> str:
        return f"sdlc:job:{job_id}"

    def create(self, job_id: str):
        data = {
            "status": JobStatus.PENDING,
            "current_step": "",
            "steps": json.dumps({step: "pending" for step in STEPS}),
            "result": "",
            "error": "",
        }
        self.client.hset(self._key(job_id), mapping=data)

    def set_running(self, job_id: str):
        self.client.hset(self._key(job_id), "status", JobStatus.RUNNING)

    def start_step(self, job_id: str, step: str):
        steps = json.loads(self.client.hget(self._key(job_id), "steps"))
        steps[step] = "running"

        self.client.hset(
            self._key(job_id),
            mapping={
                "current_step": step,
                "steps": json.dumps(steps),
            }
        )

    def complete_step(self, job_id: str, step: str):
        steps = json.loads(self.client.hget(self._key(job_id), "steps"))
        steps[step] = "completed"

        self.client.hset(
            self._key(job_id),
            "steps",
            json.dumps(steps)
        )

    def complete(self, job_id: str, result: dict):
        self.client.hset(
            self._key(job_id),
            mapping={
                "status": JobStatus.COMPLETED,
                "result": json.dumps(result),
            }
        )

    def fail(self, job_id: str, error: str):
        self.client.hset(
            self._key(job_id),
            mapping={
                "status": JobStatus.FAILED,
                "error": error,
            }
        )

    def get(self, job_id: str) -> dict | None:
        data = self.client.hgetall(self._key(job_id))
        if not data:
            return None

        return {
            "status": data["status"],
            "current_step": data["current_step"] or None,
            "steps": json.loads(data["steps"]),
            "result": json.loads(data["result"]) if data["result"] else None,
            "error": data["error"] or None,
        }
        
    def get_next_step(self, job_id: str) -> str | None:
        job = self.get(job_id)
        if not job:
            return None

        for step, status in job["steps"].items():
            if status != "completed":
                return step

        return None  # all done

    def fail_step(self, job_id: str, step: str, error: str):
        steps = json.loads(self.client.hget(self._key(job_id), "steps"))
        steps[step] = "failed"

        self.client.hset(
            self._key(job_id),
            mapping={
                "status": JobStatus.FAILED,
                "current_step": step,
                "steps": json.dumps(steps),
                "error": error,
            }
        )
