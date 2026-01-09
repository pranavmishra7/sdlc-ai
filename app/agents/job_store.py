import json
from pathlib import Path

BASE_PATH = Path("jobs")

def get_job_dir(job_id: str) -> Path:
    path = BASE_PATH / job_id
    path.mkdir(parents=True, exist_ok=True)
    return path

def save_step(job_id: str, step_name: str, data: dict):
    job_dir = get_job_dir(job_id)
    with open(job_dir / f"{step_name}.json", "w") as f:
        json.dump(data, f, indent=2)

def load_status(job_id: str) -> dict:
    path = get_job_dir(job_id) / "status.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text())

def save_status(job_id: str, status: dict):
    job_dir = get_job_dir(job_id)
    with open(job_dir / "status.json", "w") as f:
        json.dump(status, f, indent=2)
