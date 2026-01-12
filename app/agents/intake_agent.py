from app.llm.router import get_llm
from app.agents.utils import compact


def run_intake(product_idea: str) -> dict:
    if not product_idea or not product_idea.strip():
        raise ValueError("Product idea is empty")

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

    return {
        "raw_output": response
    }
