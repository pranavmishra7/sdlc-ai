from datetime import datetime
from app.llm.router import get_llm
from app.agents.safe_parser import safe_parse_json
from app.agents.utils import compact


def run_requirements(context: str) -> dict:
    llm = get_llm()

    prompt = f"""
    Return ONLY valid JSON.
    No markdown. No explanations.

    Rules:
    - Each array MUST contain at least 7 items
    - Functional requirements must be actionable
    - Non-functional requirements must be measurable
    - Constraints must be real-world limitations

    Return EXACTLY this structure:

    {{
    "functional_requirements": [
        "At least 7 functional requirements"
    ],
    "non_functional_requirements": [
        "At least 7 non-functional requirements"
    ],
    "constraints": [
        "At least 5 constraints"
    ]
    }}

    Context:
    {context}
    """

    response = llm.generate(prompt)
    parsed = safe_parse_json(response)
    return {
        "raw_output": response,
        "section": "requirements",
        "content": parsed,
        "generated_at": datetime.utcnow().isoformat(),
    }
