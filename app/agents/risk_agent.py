from datetime import datetime
from app.llm.router import get_llm
from app.agents.safe_parser import safe_parse_json
from app.agents.utils import compact


def run_risk(context: str) -> dict:
    llm = get_llm()

    prompt = f"""
    Return ONLY valid JSON.
    No markdown. No explanations.

    Rules:
    - Risks must be concrete and realistic
    - Mitigations must directly map to risks
    - Arrays must be equal length

    Return EXACTLY this structure:

    {{
    "risks": [
        "At least 6 clearly described risks"
    ],
    "mitigations": [
        "At least 6 corresponding mitigations"
    ]
    }}

    Context:
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
