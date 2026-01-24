from datetime import datetime
from app.llm.router import get_llm
from app.agents.safe_parser import safe_parse_json
from app.agents.utils import compact


def run_estimation(context: str) -> dict:
    llm = get_llm()

    prompt = f"""
    Return ONLY valid JSON.
    No markdown. No explanations.

    Rules:
    - Effort must be broken down by phase
    - Timeline must include total duration
    - Risks must be delivery-related

    Return EXACTLY this structure:

    {{
    "effort_breakdown": [
        "At least 6 phases with estimated effort"
    ],
    "timeline": "Clear end-to-end delivery timeline",
    "assumptions": [
        "At least 5 estimation assumptions"
    ],
    "risks": [
        "At least 5 delivery or estimation risks"
    ]
    }}

    Context:
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
