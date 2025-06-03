from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "test-service"

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str = "test_db"
    POSTGRES_PORT: str = "5432"
    POSTGRES_DB: str

    CANDIDATE_SERVICE_URL: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
