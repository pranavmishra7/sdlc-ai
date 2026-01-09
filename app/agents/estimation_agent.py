from datetime import datetime
from typing import Dict, Any

from app.llm.router import get_llm
from app.agents.utils import compact


def run_estimation(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    SDLC Estimation Agent
    - Pure reasoning
    - No side effects
    """

    started_at = datetime.utcnow().isoformat()
    llm = get_llm()

    intake = input_data.get("intake", {})
    scope = input_data.get("scope", {})
    requirements = input_data.get("requirements", {})
    architecture = input_data.get("architecture", {})

    prompt = f"""
    You are an SDLC project estimation agent.

    Based on the inputs below, provide effort and timeline estimation.

    Intake:
    {compact(intake)}

    Scope:
    {compact(scope)}

    Requirements:
    {compact(requirements)}

    Architecture:
    {compact(architecture)}

    Return STRICT JSON with:
    - effort_breakdown
    - estimated_timeline
    - assumptions
    - risks
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
        "step": "estimation",
        "status": "completed",
        "started_at": started_at,
        "completed_at": datetime.utcnow().isoformat(),
        "output": output
    }
