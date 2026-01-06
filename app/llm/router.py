from .ollama_client import OllamaClient
from app.config.settings import settings

def get_llm():
    return OllamaClient()
