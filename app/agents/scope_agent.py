from app.llm.router import get_llm
from app.agents.utils import compact


def run_scope(context: str) -> dict:
    llm = get_llm()

    prompt = f"""
    You are an SDLC scope definition agent.

    Based on the context below, define project scope.

    Context:
    {compact(context)}

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

    return {
        "raw_output": response
    }
