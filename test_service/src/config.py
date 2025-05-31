from pydantic import PostgresDsn
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "test-service"

    DATABASE_URL: PostgresDsn

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
