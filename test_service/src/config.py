from pydantic import PostgresDsn
from pydantic_settings import BaseSettings
from datetime import timedelta


class Settings(BaseSettings):
    PROJECT_NAME: str = "test-service"
    DATABASE_URL: PostgresDsn

    SECRET_KEY: str = "secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    @property
    def access_token_expire_timedelta(self) -> timedelta:
        return timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
