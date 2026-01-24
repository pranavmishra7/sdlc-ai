from datetime import datetime
from app.llm.router import get_llm
from app.agents.safe_parser import safe_parse_json
from app.agents.utils import compact


def run_scope(context: str) -> dict:
    llm = get_llm()

    prompt = f"""
    Return ONLY valid JSON.
    No markdown. No explanations.

    Rules:
    - Arrays MUST NOT be empty
    - Be concrete and testable
    - Avoid generic phrases like "system should"

    Return EXACTLY this structure:

    {{
    "in_scope": [
        "At least 6 specific inclusions describing what is covered"
    ],
    "out_of_scope": [
        "At least 4 explicit exclusions"
    ],
    "success_criteria": [
        "At least 5 measurable or observable success conditions"
    ]
    }}

    Context:
    {context}
    """

    response = llm.generate(prompt)
    parsed = safe_parse_json(response)
    return {
        "raw_output": response,
        "section": "scope",
        "content": parsed,
        "generated_at": datetime.utcnow().isoformat(),
    }
