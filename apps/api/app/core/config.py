from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

REPO_ROOT = Path(__file__).resolve().parents[4]
API_ROOT = Path(__file__).resolve().parents[2]


def _resolve_repo_relative_path(raw_path: str) -> Path:
    path = Path(raw_path)
    if path.is_absolute():
        return path
    return (REPO_ROOT / path).resolve()


def _normalize_database_url(database_url: str) -> str:
    prefix = "sqlite:///"

    if not database_url.startswith(prefix):
        return database_url

    raw_path = database_url[len(prefix) :]
    if raw_path == ":memory:" or raw_path.startswith("/"):
        return database_url

    resolved_path = _resolve_repo_relative_path(raw_path)
    return f"{prefix}{resolved_path.as_posix()}"


class Settings(BaseSettings):
    app_env: str = Field(default="development", alias="APP_ENV")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-5.4", alias="OPENAI_MODEL")
    openai_reasoning: str = Field(default="high", alias="OPENAI_REASONING")

    database_url: str = Field(default="sqlite:///./data/app.db", alias="DATABASE_URL")
    data_dir: str = Field(default="./data", alias="DATA_DIR")
    upload_dir: str = Field(default="./data/uploads", alias="UPLOAD_DIR")
    temp_upload_dir: str = Field(default="./data/tmp", alias="TEMP_UPLOAD_DIR")

    api_host: str = Field(default="0.0.0.0", alias="API_HOST")
    api_port: int = Field(default=8000, alias="API_PORT")

    model_config = SettingsConfigDict(
        env_file=(str(REPO_ROOT / ".env"), str(API_ROOT / ".env")),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def resolved_database_url(self) -> str:
        return _normalize_database_url(self.database_url)

    @property
    def data_dir_path(self) -> Path:
        return _resolve_repo_relative_path(self.data_dir)

    @property
    def upload_dir_path(self) -> Path:
        return _resolve_repo_relative_path(self.upload_dir)

    @property
    def temp_upload_dir_path(self) -> Path:
        return _resolve_repo_relative_path(self.temp_upload_dir)


@lru_cache
def get_settings() -> Settings:
    return Settings()
