from app.llm.router import get_llm
from app.agents.utils import compact

def run_risk(requirements: dict, architecture: dict) -> dict:
    llm = get_llm()

    prompt = f"""
    Identify risks based on requirements and architecture.

    Return JSON with:
    - technical_risks
    - delivery_risks
    - business_risks
    - mitigations

    Requirements:
    {compact(requirements)}

    Architecture:
    {compact(architecture)}
    """

    output = llm.generate(prompt)

    return {
        "raw_output": output
    }
