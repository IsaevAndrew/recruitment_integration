from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import async_session
from src.auth.service import get_current_user, get_current_admin
from src.auth.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_db():
    async with async_session() as session:
        yield session


async def authenticated_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
) -> User:
    return await get_current_user(token, db)


async def authenticated_admin(current_user: User = Depends(authenticated_user)) -> User:
    return await get_current_admin(current_user)
