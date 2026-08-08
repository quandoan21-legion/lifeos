from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "LifeOS API"
    version: str = "0.1.0"
    debug: bool = True

    DATABASE_URL: str
    LOG_LEVEL: str = "INFO"

    db_pool_size: int = 5
    db_max_overflow: int = 10
    db_pool_recycle: int = 300
    db_echo: bool = False

    class Config:
        env_file = ".env"

    @property
    def async_database_url(self) -> str:
        if self.DATABASE_URL.startswith("postgresql+psycopg://"):
            return self.DATABASE_URL.replace(
                "postgresql+psycopg://",
                "postgresql+psycopg_async://",
            )
        return self.DATABASE_URL


settings = Settings()
