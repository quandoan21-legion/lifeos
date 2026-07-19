from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "LifeOS API"
    version: str = "0.1.0"
    debug: bool = True

    class Config:
        env_file = ".env"


settings = Settings()
