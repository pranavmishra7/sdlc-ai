from typing import Any
from app.llm.ollama_client import OllamaClient
from app.config.settings import settings
from app.llm.circuit_breaker import CircuitBreaker, CircuitBreakerOpen


# -------------------------------------------------
# Circuit breakers (one per backend)
# -------------------------------------------------

ollama_breaker = CircuitBreaker(
    failure_threshold=3,
    recovery_timeout=30,
)

openai_breaker = CircuitBreaker(
    failure_threshold=3,
    recovery_timeout=30,
)


# -------------------------------------------------
# LLM Wrapper
# -------------------------------------------------

class LLMWrapper:
    """
    Wraps an LLM client with a circuit breaker.
    """

    def __init__(self, client, breaker: CircuitBreaker):
        self._client = client
        self._breaker = breaker

    def generate(self, prompt: str) -> str:
        """
        Generate text using circuit breaker protection.
        """

        def _call():
            return self._client.generate(prompt)

        try:
            return self._breaker.call(_call)

        except CircuitBreakerOpen as exc:
            # Fail fast → treated as retryable infra error
            raise RuntimeError(
                f"LLM circuit breaker open: {exc}"
            ) from exc


# -------------------------------------------------
# Router
# -------------------------------------------------

def get_llm() -> Any:
    """
    Return an LLM client wrapped with circuit breaker.
    """

    provider = settings.LLM_PROVIDER.lower()

    if provider == "ollama":
        client = OllamaClient(
            base_url=settings.OLLAMA_BASE_URL,
            model=settings.OLLAMA_MODEL,
        )
        return LLMWrapper(client, ollama_breaker)

    raise ValueError(f"Unsupported LLM provider: {provider}")
