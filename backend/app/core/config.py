from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    DATABASE_URL: str = ""
    REDIS_URL: str = "redis://localhost:6379"
    ANTHROPIC_API_KEY: str = ""
    AI_INPUT_PRICE_PER_1M_TOKENS: float = 3.0
    AI_OUTPUT_PRICE_PER_1M_TOKENS: float = 15.0
    RAW_MESSAGE_LOGGING_ENABLED: bool = True
    ENVIRONMENT: str = "development"
    MAX_MESSAGE_LENGTH: int = 10000
    CORS_ORIGINS: list = ["*"]

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
