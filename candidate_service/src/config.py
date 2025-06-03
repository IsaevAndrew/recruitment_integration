from pydantic_settings import BaseSettings
from datetime import timedelta


class Settings(BaseSettings):
    PROJECT_NAME: str = "candidate-service"

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str = "candidate_db"
    POSTGRES_PORT: str = "5432"
    POSTGRES_DB: str

    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    TEST_SERVICE_URL: str

    @property
    def access_token_expire_timedelta(self) -> timedelta:
        return timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
