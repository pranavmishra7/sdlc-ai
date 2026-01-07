from app.llm.router import get_llm
from app.agents.utils import compact

def run_sow(
    scope: dict,
    requirements: dict,
    estimation: dict,
    risks: dict
) -> str:
    llm = get_llm()

    prompt = f"""
    Create a professional Statement of Work (SOW) using the details below.

    Sections:
    - Overview
    - Scope
    - Deliverables
    - Timeline & Milestones
    - Assumptions
    - Risks
    - Commercials (no pricing, just structure)

    Scope:
    {compact(scope)}

    Requirements:
    {compact(requirements)}

    Estimation:
    {compact(estimation)}

    Risks:
    {compact(risks)}
    """

    return llm.generate(prompt)
