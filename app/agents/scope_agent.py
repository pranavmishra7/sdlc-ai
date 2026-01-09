from datetime import datetime
from typing import Dict, Any

from app.llm.router import get_llm
from app.agents.utils import compact


def run_scope(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    SDLC Scope Agent
    - Pure reasoning
    - No side effects
    """

    started_at = datetime.utcnow().isoformat()
    llm = get_llm()

    intake_output = input_data.get("intake", {})

    prompt = f"""
    You are an SDLC scope definition agent.

    Based on the intake below, define project scope.

    Intake:
    {compact(intake_output)}

    Return STRICT JSON with:
    - in_scope
    - out_of_scope
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
        "step": "scope",
        "status": "completed",
        "started_at": started_at,
        "completed_at": datetime.now().isoformat(),
        "output": output
    }
