from fastapi import HTTPException, status, Depends
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_db
from src.questions.service import QuestionService


async def get_question_service(db: AsyncSession = Depends(get_db)) -> QuestionService:
    return QuestionService(db)


async def valid_question_id(
    question_id: UUID,
    service: QuestionService = Depends(get_question_service),
) -> dict:
    question = await service.get_question(question_id)
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Question not found"
        )
    return question
