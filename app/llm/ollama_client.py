import requests
from app.config.settings import settings


class OllamaClient:
    """
    Minimal Ollama HTTP client.
    URL is always taken from settings.
    Model can be overridden if needed.
    """

    def __init__(self, model: str | None = None):
        self.url = f"{settings.OLLAMA_URL}/api/chat"
        self.model = model or settings.OLLAMA_MODEL

    def generate(self, prompt: str) -> str:
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "options": {
                "temperature": 0.2,
                "top_p": 0.9,
                "num_ctx": 2048,
                "num_predict": 200,
                "repeat_penalty": 1.1,
                "mirostat": 0,
                "stop": ["}"]
            },
            "stream": False
        }

        response = requests.post(
            self.url,
            json=payload,
            timeout=1200
        )

        if response.status_code != 200:
            raise RuntimeError(
                f"Ollama error {response.status_code}: {response.text}"
            )

        data = response.json()

        if (
            "message" not in data
            or "content" not in data["message"]
        ):
            raise RuntimeError(
                f"Unexpected Ollama response: {data}"
            )

        return data["message"]["content"]
