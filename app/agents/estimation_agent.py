from app.llm.router import get_llm
from app.agents.utils import compact
def run_estimation(requirements: dict, architecture: dict) -> dict:
    llm = get_llm()

    prompt = f"""
    Estimate effort and timeline based on requirements and architecture.

    Return JSON with:
    - effort_breakdown (by phase)
    - team_size
    - timeline_weeks
    - confidence_level

    Requirements:
    {compact(requirements)}

    Architecture:
    {compact(architecture)}
    """

    output = llm.generate(prompt)

    return {
        "raw_output": output
    }
