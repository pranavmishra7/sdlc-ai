from datetime import datetime
from app.llm.router import get_llm
from app.agents.safe_parser import safe_parse_json
from app.agents.utils import compact


def run_risk(context: str) -> dict:
    llm = get_llm()

    prompt = f"""
    Act as a senior project consultant specializing in professional services delivery.

    Your task is to generate a Delivery Estimation Summary in strict JSON format for a high-value client engagement.

    The output must:
    - Structure effort breakdown by delivery phases with a clear business purpose (e.g., Discovery, Build, UAT)
    - Express timelines as logical phase sequences using ranges (e.g., "Weeks 1–3: Requirements finalization")
    - Include only delivery-impacting assumptions (e.g., stakeholder availability, decision turnaround time)
    - List risks using mitigation-ready, client-actionable language

    REQUIRED JSON STRUCTURE:
    {{
    "effort_breakdown": [
        {{
        "phase": "Phase name",
        "purpose": "One-line delivery objective",
        "effort_ratio": "Numeric percentage of total effort (e.g., '25%')"
        }}
    ],
    "timeline": {{
        "phases": [
        {{
            "name": "Phase name",
            "duration": "Range only (e.g., '2–4 weeks')"
        }}
        ],
        "dependencies": "Concise description of critical phase handoffs"
    }},
    "assumptions": [
        "Delivery-critical assumption only",
        "Maximum 5 items"
    ],
    "risks": [
        {{
        "risk": "Clear delivery risk",
        "impact": "High | Medium | Low",
        "mitigation": "Specific, actionable mitigation approach"
        }}
    ]
    }}

    STRICT CONSTRAINTS:
    - Output MUST be valid JSON only
    - No markdown, explanations, or comments
    - No placeholder text (e.g., TBD, to be confirmed)
    - No absolute dates or guaranteed deadlines
    - No technology, platform, or vendor references
    - Effort ratios must total approximately 100%
    - Tone: Confident, realistic, and adaptable to client feedback
    
    CONTEXT:
    {context}
    """

    response = llm.generate(prompt)
    parsed = safe_parse_json(response)
    return {
        "raw_output": response,
        "section": "risk",
        "content": parsed,
        "generated_at": datetime.utcnow().isoformat(),
    }
