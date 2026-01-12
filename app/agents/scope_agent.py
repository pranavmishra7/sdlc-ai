from app.llm.router import get_llm
from app.agents.utils import compact


def run_scope(context: str) -> dict:
    if not context or not context.strip():
        raise ValueError("Context is empty for scope")

    llm = get_llm()

    prompt = f"""
Define the project scope based on the following context.

Return a clear human-readable response covering:
- In Scope
- Out of Scope
- Assumptions

Context:
{compact(context)}
"""

    response = llm.generate(prompt)

    if not response or not isinstance(response, str):
        raise RuntimeError("LLM returned invalid scope response")

    return {
        "raw_output": response
    }
