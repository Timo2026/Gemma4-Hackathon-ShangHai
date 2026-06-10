from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_BACKEND_DIR = str(Path(__file__).resolve().parent.parent.parent)


class Settings(BaseSettings):
    app_name: str = "HEDIS AI Review API"
    data_dir: str = _BACKEND_DIR
    upload_storage_dir: str = "uploads"
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/hedis_ai_review"
    llm_provider: str = "deepseek"
    llm_api_key: str = ""
    llm_base_url: str = "https://api.deepseek.com"
    llm_model_name: str = "deepseek-chat"
    llm_review_mode: str = "legacy_extraction"
    llm_timeout_seconds: float = 30.0
    allowed_origins: list[str] = ["http://localhost:3000"]

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
