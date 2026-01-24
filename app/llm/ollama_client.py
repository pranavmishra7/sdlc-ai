import requests
from app.config.settings import settings


class OllamaClient:
    """
    Minimal, SAFE Ollama HTTP client.
    Designed for structured enterprise outputs.
    """

    def __init__(self, model: str | None = None):
        self.url = f"{settings.OLLAMA_URL}/api/chat"
        self.model = model or settings.OLLAMA_MODEL

    def generate(self, prompt: str) -> str:
        print("Using Ollama model:", self.model)

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "options": {
                # 🔒 Determinism
                "temperature": 0.1,
                "top_p": 0.9,

                # 🧠 Enough context for SDLC
                "num_ctx": 4096,

                # 📏 Allow full documents
                "num_predict": 1200,

                # 🧪 Stability
                "repeat_penalty": 1.05,
                "mirostat": 0
            },

            # ❌ DO NOT STOP GENERATION MID-JSON
            # "stop": ["```"],

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

        if "message" not in data or "content" not in data["message"]:
            raise RuntimeError(f"Unexpected Ollama response: {data}")

        content = data["message"]["content"]

        # 🧹 Defensive cleanup
        return content.strip()
