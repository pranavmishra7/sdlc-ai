from datetime import datetime
from app.llm.router import get_llm
from app.agents.safe_parser import safe_parse_json
from app.agents.utils import compact


def run_sow(context: str) -> dict:
    llm = get_llm()

    prompt = f"""
   You are a senior professional services delivery consultant preparing a client-facing Statement of Work (SOW) for a regulated financial services engagement.

    Your task is to generate ONLY valid JSON output that strictly conforms to the structure defined below.

    OUTPUT RULES (MANDATORY):
    - Output pure JSON only
    - No markdown, no explanations, no comments
    - No prose outside JSON
    - No extra keys beyond those defined
    - Double quotes for all strings
    - Arrays MUST NOT be empty
    - Content must be suitable for regulated financial institutions
    - Avoid speculative language, guarantees, or advisory claims

    CONTENT GUIDELINES:
    - Deliverables must be tangible, reviewable artifacts (documents, system modules, configurations)
    - Milestones must be approval-gated phases (no absolute calendar dates)
    - Payment terms must be percentage-based and triggered by objective acceptance criteria
    - Assumptions must directly affect scope, delivery feasibility, or pricing
    - Do NOT include investment advice, performance guarantees, or automated decision-making

    REQUIRED JSON STRUCTURE (EXACT):

    {{
      "project_title": "Clear, client-facing project name",
      "deliverables": [
        "Deliverable 1 with specific, measurable characteristics",
        "Deliverable 2 with specific, measurable characteristics",
        "Additional deliverables as required"
      ],
      "milestones": [
        "Milestone name with explicit approval or sign-off criteria",
        "Milestone name with explicit approval or sign-off criteria"
      ],
      "payment_terms": "Percentage-based payments mapped to milestone acceptance (e.g., '30% upon approval of requirements documentation')",
      "assumptions": [
        "Assumption that materially impacts scope, timeline, or pricing",
        "Assumption that materially impacts scope, timeline, or pricing"
      ]
    }}

  CONSTRAINTS:
  - No absolute dates
  - No hypothetical outcomes
  - No vendor-specific commitments unless explicitly required
  - Regulatory terminology must be appropriate for financial services environments
  - Language must be precise, contractual, and enterprise-ready

  CONTEXT:
  Use all relevant context provided from prior workflow steps, including scope definition, requirements, architecture, estimation, and risk outputs.

    """

    response = llm.generate(prompt)
    parsed = safe_parse_json(response)
    return {
        "raw_output": response,
        "section": "sow",
        "content": parsed,
        "generated_at": datetime.utcnow().isoformat(),
    }
