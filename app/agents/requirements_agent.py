from app.llm.router import get_llm

def run_requirements(scope: dict) -> dict:
    llm = get_llm()

    prompt = f"""
    Convert the following scope into structured requirements.

    Return JSON with:
    - epics
    - functional_requirements
    - non_functional_requirements
    - assumptions

    Scope:
    {scope}
    """

    output = llm.generate(prompt)

    return {
        "raw_output": output
    }
