
from typing import List, Union

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "IntelliChat AI"
    APP_ENV: str = "development"
    DEBUG: bool = True
    PORT: int = 8000
    HOST: str = "0.0.0.0"

    # Security & Auth
    SECRET_KEY: str = "super-secret-production-jwt-key-change-in-production-12345678"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./chatbot.db"

    # LLM Provider Configuration
    DEFAULT_LLM_PROVIDER: str = "ollama"
    DEFAULT_MODEL: str = "qwen2.5:3b"

    GROQ_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    HUGGINGFACE_API_KEY: str = ""

    # Ollama Configuration
    OLLAMA_BASE_URL: str = "http://localhost:11434"

    # CORS
    ALLOWED_ORIGINS: Union[str, List[str]] = (
        "http://localhost:5173,"
        "http://127.0.0.1:5173,"
        "http://localhost:3000"
    )

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            return [
                origin.strip()
                for origin in v.split(",")
                if origin.strip()
            ]
        return v

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()
