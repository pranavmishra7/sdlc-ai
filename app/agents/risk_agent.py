from app.llm.router import get_llm
from app.agents.utils import compact


def run_risk(context: str) -> dict:
    llm = get_llm()

    prompt = f"""
    You are an SDLC risk analysis agent.

    Based on the context below, identify project risks.

    Context:
    {compact(context)}

    Return STRICT JSON with:
    - technical_risks
    - delivery_risks
    - operational_risks
    - mitigation_strategies
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
