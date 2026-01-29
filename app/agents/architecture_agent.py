from datetime import datetime
from app.llm.router import get_llm
from app.agents.safe_parser import safe_parse_json
from app.agents.utils import compact


def run_architecture(context: str) -> dict:
    llm = get_llm()

    prompt = f"""
    You are preparing a **Solution Architecture Overview**
    for a regulated financial services client.

    Audience includes:
    - Enterprise architects
    - Security and compliance teams
    - Business stakeholders

    STRICT RULES:
    - Output ONLY valid JSON
    - No markdown, no explanations
    - Avoid vendor or technology bias unless necessary
    - Focus on logical components and responsibilities
    - Do NOT describe automated investment decision-making
    - Frame analytics as insight and decision support

    Return EXACTLY this structure:

    {{
    "architecture_overview": "High-level description of the solution architecture and its purpose",
    "components": [
        "Major logical components and their responsibilities"
    ],
    "data_flow": [
        "Key data flows described in business-relevant terms"
    ],
    "technology_assumptions": [
        "Assumptions that materially influence architectural decisions"
    ]
    }}

    CONTEXT:
    {context}
    """

    response = llm.generate(prompt)
    parsed = safe_parse_json(response)

    return {
        "raw_output": response,
        "section": "architecture",
        "content": parsed,
        "generated_at": datetime.utcnow().isoformat(),
    }
