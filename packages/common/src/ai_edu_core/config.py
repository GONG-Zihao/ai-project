from functools import lru_cache
from typing import List

from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)

    app_name: str = "AI Education Platform"
    app_env: str = "development"
    app_debug: bool = True
    secret_key: str = "change-me"
    access_token_expire_minutes: int = 60
    algorithm: str = "HS256"

    database_url: str = "postgresql+asyncpg://ai_edu:ai_edu@db:5432/ai_edu"
    sync_database_url: str = "postgresql+psycopg://ai_edu:ai_edu@db:5432/ai_edu"

    redis_url: str = "redis://redis:6379/0"

    allowed_origins: List[AnyHttpUrl] | List[str] = ["http://localhost:3000", "http://localhost:8501"]

    default_llm_provider: str = "deepseek"
    default_llm_model: str = "deepseek-chat"
    enable_mock_ai: bool = False
    enable_local_llm: bool = False

    openai_api_key: str | None = None
    deepseek_api_key: str | None = None
    azure_openai_api_key: str | None = None
    azure_openai_endpoint: str | None = None

    qdrant_url: str = "http://qdrant:6333"
    qdrant_api_key: str | None = None

    s3_endpoint_url: str = "http://minio:9000"
    s3_access_key: str = "minioadmin"
    s3_secret_key: str = "minioadmin"
    s3_bucket: str = "ai-edu"

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def split_origins(cls, value: str | List[str]) -> List[str]:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin]
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
