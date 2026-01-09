import json
from pathlib import Path
from typing import Any, Dict, Optional, List


class JobStore:
    """
    File-based job storage.
    """

    BASE_DIR = Path("jobs")

    def __init__(self, job_id: str):
        self.job_id = job_id
        self.job_dir = self.BASE_DIR / job_id
        self.job_dir.mkdir(parents=True, exist_ok=True)

    # -------------------------
    # Write
    # -------------------------

    def save_step(self, step_name: str, data: Dict[str, Any]) -> None:
        path = self.job_dir / f"{step_name}.json"
        with path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def save_status(self, status: Dict[str, Any]) -> None:
        path = self.job_dir / "status.json"
        with path.open("w", encoding="utf-8") as f:
            json.dump(status, f, indent=2)

    # -------------------------
    # Read
    # -------------------------

    def load_step(self, step_name: str) -> Optional[Dict[str, Any]]:
        path = self.job_dir / f"{step_name}.json"
        if not path.exists():
            return None
        return json.loads(path.read_text())

    def load_status(self) -> Optional[Dict[str, Any]]:
        path = self.job_dir / "status.json"
        if not path.exists():
            return None
        return json.loads(path.read_text())

    # -------------------------
    # Admin helpers
    # -------------------------

    @classmethod
    def list_jobs(cls) -> List[str]:
        if not cls.BASE_DIR.exists():
            return []
        return [p.name for p in cls.BASE_DIR.iterdir() if p.is_dir()]

    @classmethod
    def list_dead_letter_jobs(cls) -> List[Dict[str, Any]]:
        jobs = []
        for job_id in cls.list_jobs():
            store = cls(job_id)
            status = store.load_status()
            if status and status.get("dead_letter"):
                jobs.append({
                    "job_id": job_id,
                    "dead_letter": status["dead_letter"],
                })
        return jobs
