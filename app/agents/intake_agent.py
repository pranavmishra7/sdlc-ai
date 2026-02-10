from datetime import datetime
from app.llm.router import get_llm
from app.agents.safe_parser import safe_parse_json
from app.agents.utils import compact
from logging import getLogger

logger = getLogger(__name__)


def run_intake(product_idea: str) -> dict:
    llm = get_llm()

    prompt = f"""
    Create a precise financial services discovery summary in JSON format for a senior management consultant.

    The summary must:

    1. Clearly articulate the business problem at an executive level
    2. Detail specific operational challenges using business language only
    3. Outline material business impacts based on observed or documented issues
    4. Define primary and secondary user roles
    5. List critical assumptions and dependencies
    6. Explicitly state out-of-scope items to establish clear boundaries

    JSON STRUCTURE REQUIREMENTS:
    {{
    "problem_statement": {{
        "overview": "Concise executive-level problem description (1–2 sentences)",
        "current_challenges": [
        "Operational pain point stated in non-technical, business language",
        "Maximum 5 items"
        ],
        "business_impact": [
        "Observed business impact (cost, risk, delay, compliance, efficiency)",
        "No speculative or future projections"
        ]
    }},
    "target_users": {{
        "primary_users": [
        "Core business roles directly affected",
        "Limit to 3–5 clearly defined positions"
        ],
        "secondary_users": [
        "Oversight, governance, or control functions",
        "Maximum 3 roles"
        ]
    }},
    "assumptions": [
        "Critical dependency or condition",
        "Maximum 3 items"
    ],
    "out_of_scope": [
        "Explicitly excluded capability or responsibility",
        "Neutral phrasing (no negative or defensive language)",
        "3–5 clear exclusions"
    ]
    }}

    STRICT FORMATTING RULES:
    - Output MUST be valid JSON only
    - No markdown, explanations, or comments
    - No placeholder text (e.g., TBD, various, to be confirmed)
    - No technical jargon, system names, or implementation details
    - Key names must match exactly as specified
    - Double quotes for all strings
    - Proper JSON escaping
    
    CONTEXT:
    {product_idea}
    """

    response = llm.generate(prompt)
    parsed = safe_parse_json(response)
    logger.info(f"--Intake Agent Output: parser started--")
    logger.info(f"Intake Agent Output: parser={parsed}")
    logger.info(f"--Intake Agent Output: parser ended--")
    return {
        "raw_output": response,
        "section": "intake",
        "content": parsed,
        "generated_at": datetime.utcnow().isoformat(),
    }
