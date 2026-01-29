from datetime import datetime
from app.llm.router import get_llm
from app.agents.safe_parser import safe_parse_json
from app.agents.utils import compact


def run_requirements(context: str) -> dict:
    llm = get_llm()

    prompt = f"""
    You are preparing a **Business Requirements Document (BRD)**
    for a financial services engagement.

    These requirements must be suitable for:
    - Design and implementation
    - Compliance review
    - User acceptance testing (UAT)

    STRICT RULES:
    - Output ONLY valid JSON
    - No markdown, no explanations
    - No placeholders or vague phrasing
    - No automated investment advice or decision execution
    - Requirements must be testable and unambiguous
    - Express capabilities as decision support, not decision automation

    Return EXACTLY this structure:

    {{
    "functional_requirements": [
        "User-facing or business-facing capabilities stated as verifiable requirements"
    ],
    "non_functional_requirements": [
        "Measurable performance, security, compliance, or availability requirements"
    ],
    "constraints": [
        "Known limitations, dependencies, or external constraints"
    ]
    }}

    CONTEXT:
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
