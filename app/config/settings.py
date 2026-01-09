from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # -------------------------------------------------
    # LLM Provider
    # -------------------------------------------------
    # ollama | openai
    LLM_PROVIDER: str = "ollama"

    # -------------------------------------------------
    # Ollama
    # -------------------------------------------------
    # keep both names for backward compatibility
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.2:3b"

    # -------------------------------------------------
    # Redis / Celery
    # -------------------------------------------------
    REDIS_URL: str = "redis://localhost:6379/0"

    # class Config:
    #     env_file = ".env"
    #     extra = "ignore"


settings = Settings()
