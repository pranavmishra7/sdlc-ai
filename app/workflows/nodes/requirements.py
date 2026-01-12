from app.llm.router import get_llm
from app.agents.utils import compact


def run_requirements(context: str) -> dict:
    llm = get_llm()

    prompt = f"""
    You are an SDLC requirements analysis agent.

    Based on the context below, derive requirements.

    Context:
    {compact(context)}

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

    return {
        "raw_output": response
    }
