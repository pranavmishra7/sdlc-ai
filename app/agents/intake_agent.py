from app.llm.router import get_llm

def run_intake(product_idea: str) -> dict:
    llm = get_llm()

    prompt = f"""
    Validate and structure this product idea.
    Return JSON with:
    - problem
    - target_users
    - assumptions

    Product Idea:
    {product_idea}
    """

    output = llm.generate(prompt)

    return {
        "raw_output": output
    }
