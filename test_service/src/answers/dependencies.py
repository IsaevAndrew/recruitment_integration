from fastapi import HTTPException, status, Depends
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_db
from src.answers.service import AnswerService


async def get_answer_service(
        db: AsyncSession = Depends(get_db)) -> AnswerService:
    return AnswerService(db)


async def valid_answer_id(
        answer_id: UUID,
        service: AnswerService = Depends(get_answer_service),
) -> dict:
    answer = await service.get_answer(answer_id)
    if not answer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Answer not found")
    return answer
