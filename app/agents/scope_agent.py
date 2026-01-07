from app.llm.router import get_llm
from app.state.job_state import JobStatus
from app.storage.job_store import JobStore


def run_scope(intake: dict, job_id: str | None = None) -> dict:
    llm = get_llm()

    prompt = f"""
You are an SDLC scope generator.

Input:
{intake}

Output STRICT JSON:
{{
  "in_scope": [string],
  "out_of_scope": [string],
  "assumptions": [string],
  "dependencies": [string],
  "constraints": [string]
}}

Rules:
- No explanations
- Max 10 items per array
- Short bullet phrases only
"""

    output = llm.generate(prompt)

    # ✅ NEW: persist state if job_id is provided
    if job_id:
        job_store = JobStore()
        job_state = job_store.get(job_id) or JobState(job_id)

        job_state.current_step = "scope"
        job_state.progress = 40
        job_state.data["scope"] = output

        job_store.save(job_state)

    return {
        "raw_output": output
    }
