from fastapi import HTTPException, status, Depends
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_db
from src.sessions.service import SessionService


async def get_session_service(db: AsyncSession = Depends(get_db)) -> SessionService:
    return SessionService(db)


async def valid_session_id(
    session_id: UUID,
    service: SessionService = Depends(get_session_service),
) -> dict:
    session = await service.get_session(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
        )
    return session
