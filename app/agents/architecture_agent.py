from datetime import datetime
from app.llm.router import get_llm
from app.agents.safe_parser import safe_parse_json
from app.agents.utils import compact


def run_architecture(context: str) -> dict:
    llm = get_llm()

    prompt = f"""
    Return ONLY valid JSON.
    No markdown. No explanations.

    Rules:
    - All arrays MUST have at least 5 items
    - Components must be logical, not just tools
    - Data flow must describe movement between components
    - Technology stack must be realistic but not vendor-locked

    Return EXACTLY this structure:

    {{
    "architecture_overview": "3–4 sentence high-level architecture description",
    "components": [
        "At least 6 logical system components"
    ],
    "data_flow": [
        "At least 5 clear data flow steps"
    ],
    "technology_stack": [
        "At least 6 technologies or platform categories"
    ],
    "assumptions": [
        "At least 5 architecture assumptions"
    ]
    }}

    Context:
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
