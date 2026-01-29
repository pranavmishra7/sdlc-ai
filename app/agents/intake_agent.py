from datetime import datetime
from app.llm.router import get_llm
from app.agents.safe_parser import safe_parse_json
from app.agents.utils import compact
from logging import getLogger

logger = getLogger(__name__)


def run_intake(product_idea: str) -> dict:
    llm = get_llm()

    prompt = f"""
    You are a senior management consultant preparing a **Discovery Summary**
    for a regulated financial services client.

    This content is intended for:
    - Executive stakeholders
    - Compliance and risk teams
    - Program sponsors

    STRICT RULES:
    - Output ONLY valid JSON
    - No markdown, no explanations
    - No speculative metrics (e.g. revenue %, user counts)
    - No promises of outcomes or performance
    - Avoid phrases like "the system will" or "automated decision-making"
    - Use neutral, professional, client-facing language

    Return EXACTLY this structure:

    {{
    "problem_statement": {{
        "overview": "Clear, executive-level articulation of the business problem",
        "current_challenges": [
        "Specific, observable operational or business challenges"
        ],
        "business_impact": [
        "Material impacts expressed in business or operational terms"
        ]
    }},
    "target_users": {{
        "primary_users": [
        "Clearly defined business or operational roles"
        ],
        "secondary_users": [
        "Governance, oversight, or supporting roles"
        ]
    }},
    "assumptions": [
        "Operational or dependency assumptions that influence scope or delivery"
    ],
    "out_of_scope": [
        "Explicit exclusions to avoid ambiguity or scope expansion"
    ]
    }}

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
