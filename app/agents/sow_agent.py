from datetime import datetime
from typing import Dict, Any

from app.llm.router import get_llm
from app.agents.utils import compact


def run_sow(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    SDLC Statement of Work (SOW) Agent
    - Pure reasoning
    - No side effects
    """

    started_at = datetime.utcnow().isoformat()
    llm = get_llm()

    intake = input_data.get("intake", {})
    scope = input_data.get("scope", {})
    requirements = input_data.get("requirements", {})
    architecture = input_data.get("architecture", {})
    estimation = input_data.get("estimation", {})
    risk = input_data.get("risk", {})

    prompt = f"""
    You are an SDLC Statement of Work (SOW) generation agent.

    Using the full SDLC context below, generate a professional SOW.

    Intake:
    {compact(intake)}

    Scope:
    {compact(scope)}

    Requirements:
    {compact(requirements)}

    Architecture:
    {compact(architecture)}

    Estimation:
    {compact(estimation)}

    Risks:
    {compact(risk)}

    Return STRICT JSON with:
    - project_overview
    - scope_of_work
    - deliverables
    - milestones
    - timeline
    - assumptions
    - exclusions
    """

    response = llm.generate(prompt)

    if response is None:
        raise RuntimeError("LLM returned None")

    if not isinstance(response, str):
        raise TypeError(f"LLM returned non-string response: {type(response)}")

    if not response.strip():
        raise RuntimeError("LLM returned empty response")

    output = {
        "raw_output": response
    }

    return {
        "step": "sow",
        "status": "completed",
        "started_at": started_at,
        "completed_at": datetime.utcnow().isoformat(),
        "output": output
    }
