"""
Pre-warm Ollama model so first real request is fast.
Run using: python -m scripts.warm_models
"""

from app.llm.router import get_llm

def warm():
    llm = get_llm()

    print("Warming Ollama model...")
    response = llm.generate("Respond with one word only: READY")
    print("Model response:", response)
    print("Ollama warm-up complete.")

if __name__ == "__main__":
    warm()
