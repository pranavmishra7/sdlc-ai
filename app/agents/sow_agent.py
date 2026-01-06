from app.llm.router import get_llm

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
    {scope}

    Requirements:
    {requirements}

    Estimation:
    {estimation}

    Risks:
    {risks}
    """

    return llm.generate(prompt)
