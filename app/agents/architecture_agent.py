from datetime import datetime
from typing import Dict, Any

from app.llm.router import get_llm
from app.agents.utils import compact


def run_architecture(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    SDLC Architecture Agent
    - Pure reasoning
    - No side effects
    """

    started_at = datetime.utcnow().isoformat()
    llm = get_llm()

    intake = input_data.get("intake", {})
    scope = input_data.get("scope", {})
    requirements = input_data.get("requirements", {})

    prompt = f"""
    You are an SDLC system architecture agent.

    Based on the inputs below, design a high-level architecture.

    Intake:
    {compact(intake)}

    Scope:
    {compact(scope)}

    Requirements:
    {compact(requirements)}

    Return STRICT JSON with:
    - architecture_overview
    - major_components
    - data_flow
    - technology_choices
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
        "step": "architecture",
        "status": "completed",
        "started_at": started_at,
        "completed_at": datetime.utcnow().isoformat(),
        "output": output
    }
