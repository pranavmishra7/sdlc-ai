from app.llm.router import get_llm
from app.agents.utils import compact


def run_sow(context: str) -> dict:
    llm = get_llm()

    prompt = f"""
    You are an SDLC Statement of Work (SOW) generation agent.

    Using the full context below, generate a professional SOW.

    Context:
    {compact(context)}

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

    return {
        "raw_output": response
    }
