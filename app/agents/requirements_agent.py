from datetime import datetime
from app.llm.router import get_llm
from app.agents.safe_parser import safe_parse_json
from app.agents.utils import compact


def run_requirements(context: str) -> dict:
    llm = get_llm()

    prompt = f"""
    Act as a senior financial services requirements architect.


    Generate a Business Requirements Document (BRD) in strict JSON format for a regulated financial services application.

    STRICT RULES:
    - Output MUST be valid JSON only
    - No markdown, explanations, or commentary
    - All requirements must be testable and objectively verifiable
    - Use active voice and precise language
    - Every functional requirement MUST start with: "The system shall..."
    - Explicitly prohibit automated decision-making or autonomous actions
    - Do NOT include solution design or implementation details

    Return EXACTLY the following JSON structure:

    {{
    "functional_requirements": [
        "The system shall ...",
        "The system shall ..."
    ],
    "non_functional_requirements": [
        "Performance, security, availability, or compliance requirement",
        "Each item must include measurable criteria"
    ],
    "constraints": [
        "External dependency, regulatory constraint, or delivery limitation",
        "Must be factual and non-speculative"
    ]
    }}

    CONTENT QUALITY REQUIREMENTS:
    - Functional requirements must describe observable system behavior
    - Non-functional requirements must include measurable thresholds
    - Constraints must reflect real-world regulatory, organizational, or technical limits
    - No future promises, assumptions, or marketing language
    - All content must be appropriate for audit and compliance review

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
