from datetime import datetime
from app.llm.router import get_llm
from app.agents.safe_parser import safe_parse_json
from app.agents.utils import compact


def run_sow(context: str) -> dict:
    llm = get_llm()

    prompt = f"""
    Return ONLY valid JSON.
    No markdown. No explanations.

    Rules:
    - Deliverables must be tangible
    - Milestones must be outcome- or time-based
    - Payment terms must be explicit

    Return EXACTLY this structure:

    {{
    "deliverables": [
        "At least 6 concrete deliverables"
    ],
    "milestones": [
        "At least 5 project milestones"
    ],
    "payment_terms": "Clear payment structure and trigger conditions",
    "assumptions": [
        "At least 5 commercial or delivery assumptions"
    ]
    }}

    Context:
    {context}
    """

    response = llm.generate(prompt)
    parsed = safe_parse_json(response)
    return {
        "raw_output": response,
        "section": "sow",
        "content": parsed,
        "generated_at": datetime.utcnow().isoformat(),
    }
