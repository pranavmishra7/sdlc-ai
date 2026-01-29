from datetime import datetime
from app.llm.router import get_llm
from app.agents.safe_parser import safe_parse_json
from app.agents.utils import compact


def run_sow(context: str) -> dict:
    llm = get_llm()

    prompt = f"""
    You are preparing a **Statement of Work (SOW)**
    for a professional services engagement in financial services.

    This content may be reviewed by:
    - Legal and procurement teams
    - Client sponsors
    - Delivery leadership

    STRICT RULES:
    - Output ONLY valid JSON
    - No markdown, no explanations
    - Deliverables must be tangible and reviewable
    - Milestones must represent client-approvable checkpoints
    - Avoid absolute terms (e.g. "fully functional")
    - Payment terms must be clear and conditional

    Return EXACTLY this structure:

    {{
    "deliverables": [
        "Concrete artifacts or outcomes to be delivered"
    ],
    "milestones": [
        "Client-reviewable delivery checkpoints"
    ],
    "payment_terms": "Clear payment structure with defined trigger conditions",
    "assumptions": [
        "Commercial or operational assumptions affecting scope or pricing"
    ]
    }}

    CONTEXT:
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
