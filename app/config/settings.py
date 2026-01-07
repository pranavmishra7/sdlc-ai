from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    OLLAMA_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.2:3b"
    REDIS_URL: str = "redis://localhost:6379/0"

    # class Config:
    #     env_file = ".env"
    #     extra = "ignore"

settings = Settings()
