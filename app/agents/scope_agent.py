from app.llm.router import get_llm

def run_scope(intake: dict) -> dict:
    llm = get_llm()

    prompt = f"""
    Based on the validated product intake below, define the project scope.

    Return JSON with:
    - in_scope
    - out_of_scope
    - constraints
    - success_criteria

    Intake:
    {intake}
    """

    output = llm.generate(prompt)

    return {
        "raw_output": output
    }
