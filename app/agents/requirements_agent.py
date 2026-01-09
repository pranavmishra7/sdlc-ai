from datetime import datetime
from typing import Dict, Any

from app.llm.router import get_llm
from app.agents.utils import compact


def run_requirements(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    SDLC Requirements Agent
    - Pure reasoning
    - No side effects
    """

    started_at = datetime.now().isoformat()
    llm = get_llm()

    intake = input_data.get("intake", {})
    scope = input_data.get("scope", {})

    prompt = f"""
    You are an SDLC requirements analysis agent.

    Based on the intake and scope below, derive requirements.

    Intake:
    {compact(intake)}

    Scope:
    {compact(scope)}

    Return STRICT JSON with:
    - functional_requirements
    - non_functional_requirements
    - assumptions
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
        "step": "requirements",
        "status": "completed",
        "started_at": started_at,
        "completed_at": datetime.now().isoformat(),
        "output": output
    }
