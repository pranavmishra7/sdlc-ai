from datetime import datetime
from app.agents.safe_parser import safe_parse_json
from app.llm.router import get_llm


def run_document_synthesis(context: dict) -> dict:
    llm = get_llm()

    prompt = f"""
You are a senior management consultant preparing a CLIENT-FACING enterprise document.

Your task is to synthesize the structured planning inputs below into a
clear, professional, executive-ready document.

Audience:
- CXOs
- Business stakeholders
- Procurement and legal teams

Writing rules:
- Use professional consulting language
- Write in complete paragraphs (no bullet dumping)
- Do NOT mention internal steps like "intake", "scope", etc.
- Do NOT include placeholders or instructional phrases
- Be concise, confident, and neutral
- Assume this will be shared externally with a client

Return STRICT JSON with EXACTLY the following structure:

{{
  "document_title": "",
  "executive_summary": "",
  "problem_statement": "",
  "solution_overview": "",
  "scope_of_work": "",
  "delivery_approach": "",
  "architecture_summary": "",
  "timeline_and_estimation": "",
  "commercials_and_payment_terms": "",
  "risks_and_mitigations": "",
  "assumptions_and_exclusions": ""
}}

Planning Inputs:
{context}
"""

    response = llm.generate(prompt)
    parsed = safe_parse_json(response)
    return {
        "raw_output": response,
        "section": "client_document",
        "content": {"document": response},
        "generated_at": datetime.utcnow().isoformat(),
    }
