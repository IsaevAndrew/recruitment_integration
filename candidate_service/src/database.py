from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from src.config import settings

engine = create_async_engine(
    str(settings.DATABASE_URL),
    echo=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Базовый класс для всех декларативных моделей
Base = declarative_base()
