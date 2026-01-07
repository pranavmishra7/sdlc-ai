from app.llm.router import get_llm
from app.agents.utils import compact
def run_architecture(requirements: dict) -> dict:
    llm = get_llm()

    prompt = f"""
    Design a high-level system architecture based on the requirements below.

    Return JSON with:
    - architecture_overview
    - components
    - data_flow
    - technology_stack
    - key_design_decisions

    Requirements:
    {compact(requirements)}
    """

    output = llm.generate(prompt)

    return {
        "raw_output": output
    }
