from app.llm.router import get_llm

llm = get_llm()

prompt = """
Return ONLY valid JSON.
No explanation.

{
  "test": "ok",
  "list": [1,2,3]
}
"""

print(llm.generate(prompt))