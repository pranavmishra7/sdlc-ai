from datetime import datetime
from typing import Dict, Any

from app.llm.router import get_llm
from app.agents.utils import compact


def run_intake(product_idea: str) -> Dict[str, Any]:
    """
    SDLC Intake Agent
    - Pure LLM reasoning
    - No side effects
    - Returns standardized step output
    """

    if not product_idea or not product_idea.strip():
        raise ValueError("Product idea is empty")

    started_at = datetime.utcnow().isoformat()
    llm = get_llm()

    prompt = f"""
    Validate and structure this product idea.
    Return STRICT JSON with:
    - problem
    - target_users
    - assumptions

    Product Idea:
    {compact(product_idea)}
    """

    response = llm.generate(prompt)

    if response is None:
        raise RuntimeError("LLM returned None")

    if not isinstance(response, str):
        raise TypeError(f"LLM returned non-string response: {type(response)}")

    if not response.strip():
        raise RuntimeError("LLM returned empty response")

    # NOTE:
    # We keep raw_output for traceability.
    # Parsing (if needed) can be added later safely.
    output = {
        "raw_output": response
    }

    return {
        "step": "intake",
        "status": "completed",
        "started_at": started_at,
        "completed_at": datetime.utcnow().isoformat(),
        "output": output
    }
