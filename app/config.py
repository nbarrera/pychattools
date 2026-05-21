from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    redis_url: str
    ollama_base_url: str
    ollama_model: str
    llm_api_key: str = "ollama"

    model_config = {"env_file": ".env"}

settings = Settings()