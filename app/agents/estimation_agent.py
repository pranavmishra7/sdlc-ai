from datetime import datetime
from app.llm.router import get_llm
from app.agents.safe_parser import safe_parse_json
from app.agents.utils import compact


def run_estimation(context: str) -> dict:
    llm = get_llm()

    prompt = f"""
    You are preparing a **Delivery Estimation Summary**
    for a professional services engagement.

    This estimate supports:
    - Planning and budgeting
    - Resource allocation
    - Commercial discussions

    STRICT RULES:
    - Output ONLY valid JSON
    - No markdown, no explanations
    - Avoid exact dates or guarantees
    - Express effort in phases with rationale
    - Clearly separate assumptions from risks

    Return EXACTLY this structure:

    {{
    "effort_breakdown": [
        "Delivery phases with purpose and relative effort"
    ],
    "timeline": "High-level delivery timeline expressed as phases or ranges",
    "assumptions": [
        "Assumptions that directly influence effort, duration, or cost"
    ],
    "risks": [
        "Delivery-related risks that may impact schedule or effort"
    ]
    }}

    CONTEXT:
    {context}
    """

    response = llm.generate(prompt)
    parsed = safe_parse_json(response)
    return {
        "raw_output": response,
        "section": "estimation",
        "content": parsed,
        "generated_at": datetime.utcnow().isoformat(),
    }
