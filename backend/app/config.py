from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Sales Insight Automator"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:5173,http://localhost:3000,http://localhost"

    # AI Engine (Groq)
    GROQ_API_KEY: str = ""
    AI_MODEL: str = "llama-3.3-70b-versatile"

    # Email (SMTP SSL)
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 465
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_NAME: str = "Rabbitt AI Sales Insights"

    # Rate Limiting
    RATE_LIMIT: str = "10/minute"

    # File Upload
    MAX_FILE_SIZE_MB: int = 10

    model_config = {"env_file": ".env", "extra": "ignore"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
