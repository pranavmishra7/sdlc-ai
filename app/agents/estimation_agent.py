from app.llm.router import get_llm
from app.agents.utils import compact


def run_estimation(context: str) -> dict:
    llm = get_llm()

    prompt = f"""
    You are an SDLC project estimation agent.

    Based on the context below, provide effort and timeline estimation.

    Context:
    {compact(context)}

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

    return {
        "raw_output": response
    }
