from datetime import datetime
from app.llm.router import get_llm
from app.agents.safe_parser import safe_parse_json
from app.agents.utils import compact


def run_architecture(context: str) -> dict:
    llm = get_llm()

    prompt = f"""
    Act as a senior enterprise solution architect designing a logical architecture for a regulated financial services client.

    Your task is to generate a structured Solution Architecture Overview that explains system boundaries, major components, and data flows at an enterprise level.

    STRICT RULES:
    - Output MUST be valid JSON only
    - No markdown, commentary, or explanations
    - No placeholders or generic filler
    - No automated investment decision-making
    - Analytics must be described as insight or decision-support only
    - Avoid vendor, cloud, or product bias unless architecturally unavoidable
    - Use business-relevant language understandable by both technical and non-technical stakeholders

    Return EXACTLY the following JSON structure:

    {{
      "architecture_overview": "Concise description of the architecture purpose, scope, and guiding principles",
      "components": [
        "Component name – primary responsibility",
        "Component name – primary responsibility"
      ],
      "data_flow": [
        "Clear, business-relevant description of how data moves between components",
        "Focus on data ownership, validation, and handoff points"
      ],
      "technology_assumptions": [
        "Architecturally significant assumption that impacts design or delivery",
        "Avoid speculative or implementation-level details"
      ]
    }}

    CONTENT QUALITY REQUIREMENTS:
    - Components must represent logical system boundaries
    - Data flows must describe what data moves and why, not protocols
    - Assumptions must be explicit, realistic, and delivery-impacting
    - All content must be suitable for regulated financial environments
    
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
