from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool
from sqlalchemy import text
from src.config import settings

engine = create_async_engine(
    str(settings.DATABASE_URL),
    echo=True,
    future=True,
    poolclass=NullPool
)

async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

Base = declarative_base()


async def get_db():
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    async with engine.begin() as conn:
        await conn.execute(text("SET search_path = public"))
        await conn.run_sync(Base.metadata.create_all)
