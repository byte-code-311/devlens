from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "sqlite:///./devlens.db"
    openai_api_key: str | None = None
    openai_model: str = "gpt-5"

    model_config = SettingsConfigDict(env_file=Path(__file__).parents[2] / ".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
