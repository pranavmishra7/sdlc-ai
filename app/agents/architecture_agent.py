from app.llm.router import get_llm
from app.agents.utils import compact


def run_architecture(context: str) -> dict:
    llm = get_llm()

    prompt = f"""
    You are an SDLC system architecture agent.

    Based on the context below, design a high-level architecture.

    Context:
    {compact(context)}

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

    return {
        "raw_output": response
    }
