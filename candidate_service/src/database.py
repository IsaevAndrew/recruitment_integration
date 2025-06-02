from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import text
from src.config import settings

engine = create_async_engine(
    str(settings.DATABASE_URL),
    echo=True,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    connect_args={"server_settings": {"search_path": "public"}}
)

async_session = sessionmaker(
    bind=engine,
    class_=AsyncSession,

)

Base = declarative_base()


async def get_db() -> AsyncSession:
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    async with engine.begin() as conn:
        await conn.execute(text("SET search_path = public"))
        await conn.run_sync(Base.metadata.create_all)
