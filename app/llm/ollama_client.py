import requests
from app.config.settings import settings
from .base import BaseLLM

class OllamaClient(BaseLLM):
    def generate(self, prompt: str) -> str:
        response = requests.post(
            f"{settings.OLLAMA_URL}/api/chat",
            json={
                "model": settings.OLLAMA_MODEL,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "stream": False
            },
            timeout=120
        )

        response.raise_for_status()
        data = response.json()

        if "error" in data:
            raise RuntimeError(f"Ollama error: {data['error']}")

        if "message" not in data or "content" not in data["message"]:
            raise RuntimeError(f"Unexpected Ollama response: {data}")

        return data["message"]["content"].strip()
