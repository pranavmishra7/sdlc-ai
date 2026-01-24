from datetime import datetime
from app.llm.router import get_llm
from app.agents.safe_parser import safe_parse_json
from app.agents.utils import compact
from logging import getLogger

logger = getLogger(__name__)


def run_intake(product_idea: str) -> dict:
    llm = get_llm()

    prompt = f"""
    You are a senior product consultant preparing a client-facing discovery summary.

    Rules:
    - Use precise, professional business language
    - Be specific, not generic
    - No marketing fluff
    - No implementation or technology assumptions
    - Output MUST be valid JSON only
    - No markdown, no explanations
    - No empty arrays

    Return EXACTLY this JSON structure:

    {{
    "problem_statement": {{
        "overview": "1–2 sentence clear business problem description",
        "current_challenges": [
        "At least 4 concrete pain points"
        ],
        "business_impact": [
        "At least 4 measurable or observable impacts"
        ]
    }},
    "target_users": {{
        "primary_users": [
        "At least 4 clearly defined primary user roles"
        ],
        "secondary_users": [
        "At least 3 supporting or indirect user role"
        ]
    }},
    "assumptions": [
        "At least 5 explicit assumptions"
    ],
    "out_of_scope": [
        "At least 3 explicitly excluded items"
    ]
    }}

    Product Idea:
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
