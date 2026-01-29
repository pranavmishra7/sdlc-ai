from datetime import datetime
from app.llm.router import get_llm
from app.agents.safe_parser import safe_parse_json
from app.agents.utils import compact


def run_scope(context: str) -> dict:
    llm = get_llm()

    prompt = f"""
    You are defining the **engagement scope** for a professional services contract
    in a regulated financial services environment.

    STRICT RULES:
    - Output ONLY valid JSON
    - No markdown, no explanations
    - Each in-scope item must be a concrete deliverable or bounded capability
    - Out-of-scope items must clearly limit liability
    - Success criteria must be objectively verifiable
    - Do NOT include business outcomes outside delivery control

    Return EXACTLY this structure:

    {{
    "in_scope": [
        "Clearly bounded deliverables or capabilities included in the engagement"
    ],
    "out_of_scope": [
        "Explicit exclusions not covered by this engagement"
    ],
    "success_criteria": [
        "Objective conditions used to confirm successful delivery"
    ]
    }}

    CONTEXT:
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
