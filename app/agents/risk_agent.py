from datetime import datetime
from app.llm.router import get_llm
from app.agents.safe_parser import safe_parse_json
from app.agents.utils import compact


def run_risk(context: str) -> dict:
    llm = get_llm()

    prompt = f"""
    You are preparing a **Project Risk Register**
    for a financial services engagement.

    This register will be reviewed by:
    - Program governance
    - Compliance teams
    - Client stakeholders

    STRICT RULES:
    - Output ONLY valid JSON
    - No markdown, no explanations
    - Risks must be realistic and specific
    - Mitigations must be actionable and proportional
    - Avoid speculative or generic risks

    Return EXACTLY this structure:

    {{
    "risks": [
        "Clearly articulated delivery, operational, or compliance risks"
    ],
    "mitigations": [
        "Concrete actions to reduce likelihood or impact of the listed risks"
    ]
    }}

    CONTEXT:
    {context}
    """

    response = llm.generate(prompt)
    parsed = safe_parse_json(response)
    return {
        "raw_output": response,
        "section": "risk",
        "content": parsed,
        "generated_at": datetime.utcnow().isoformat(),
    }
