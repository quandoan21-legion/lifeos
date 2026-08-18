from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Walk up from this file to find the project root containing .env
_PROJECT_ROOT = Path(__file__).resolve().parents[3]
_ENV_FILE = _PROJECT_ROOT / ".env"


class Settings(BaseSettings):
    app_name: str = "LifeOS API"
    version: str = "0.1.0"
    debug: bool = True

    DATABASE_URL: str
    LOG_LEVEL: str = "INFO"

    SECRET_KEY: str = "dev-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    db_pool_size: int = 5
    db_max_overflow: int = 10
    db_pool_recycle: int = 300
    db_echo: bool = False

    app_port: int = 8000

    KOREADER_DB_PATH: str | None = None
    GITHUB_TOKEN: str | None = None
    GITHUB_USERNAME: str | None = None

    ingest_email: str = ""
    ingest_password: str = ""

    model_config = SettingsConfigDict(env_file=str(_ENV_FILE), extra="ignore")

    @property
    def async_database_url(self) -> str:
        if self.DATABASE_URL.startswith("postgresql+psycopg://"):
            return self.DATABASE_URL.replace(
                "postgresql+psycopg://",
                "postgresql+psycopg_async://",
            )
        return self.DATABASE_URL


settings = Settings()
