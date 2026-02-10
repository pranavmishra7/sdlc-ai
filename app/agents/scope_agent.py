from datetime import datetime
from app.llm.router import get_llm
from app.agents.safe_parser import safe_parse_json
from app.agents.utils import compact


def run_scope(context: str) -> dict:
    llm = get_llm()

    prompt = f"""
    Act as a senior professional services consultant delivering scope documentation for a regulated financial services engagement.

    Your task is to generate a STRICTLY VALID JSON object defining the engagement scope.

    TARGET AUDIENCE:
    - Client procurement teams
    - Legal and compliance reviewers
    - Delivery and project management stakeholders

    OBJECTIVE:
    Clearly define what is included, excluded, and how success will be measured, in a way suitable for contractual agreement.

    OUTPUT RULES (MANDATORY):
    - Output PURE JSON ONLY
    - No markdown, comments, or explanatory text
    - No narrative prose outside listed items
    - Use double quotes for all strings
    - Ensure valid JSON syntax
    - Do NOT include any fields beyond those specified

    CONTENT CONSTRAINTS:
    - Include ONLY deliverables directly under provider control
    - Avoid aspirational or outcome-based language
    - No financial advice, recommendations, or guarantees
    - No speculative or hypothetical statements
    - No automated decision-making references
    - Use neutral, contractual wording

    OUTPUT STRUCTURE (EXACT):

    {{
    "in_scope": [
        "Clearly defined, tangible deliverables or services",
        "Each item must be specific, testable, and actionable"
    ],
    "out_of_scope": [
        "Explicit exclusions to prevent scope ambiguity",
        "Phrase as neutral boundary statements"
    ],
    "success_criteria": [
        "Objective and verifiable acceptance conditions",
        "Metrics must be measurable and auditable"
    ]
    }}

    QUALITY BAR:
    - Each list should contain 3–6 items
    - Avoid duplication across sections
    - Wording must be suitable for inclusion in a Statement of Work
    - Ensure consistency with regulated financial services environments

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
