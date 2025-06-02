from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import async_session
from src.questions.models import Question
from src.questions.schemas import QuestionCreate, QuestionUpdate, QuestionRead

class QuestionService:
    @staticmethod
    async def create(template_id: UUID, data: QuestionCreate) -> QuestionRead:
        async with async_session() as db:
            question = Question(**data.model_dump())
            db.add(question)
            await db.commit()
            await db.refresh(question)
            return question

    @staticmethod
    async def get_all(template_id: UUID, skip: int = 0, limit: int = 100) -> List[QuestionRead]:
        async with async_session() as db:
            result = await db.execute(
                select(Question)
                .where(Question.test_id == template_id)
                .offset(skip)
                .limit(limit)
            )
            return result.scalars().all()

    @staticmethod
    async def get_by_id(template_id: UUID, question_id: UUID) -> Optional[QuestionRead]:
        async with async_session() as db:
            result = await db.execute(
                select(Question)
                .where(Question.test_id == template_id)
                .where(Question.id == question_id)
            )
            return result.scalar_one_or_none()

    @staticmethod
    async def update(template_id: UUID, question_id: UUID, data: QuestionUpdate) -> Optional[QuestionRead]:
        async with async_session() as db:
            question = await QuestionService.get_by_id(template_id, question_id)
            if not question:
                return None
            
            update_data = data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(question, field, value)
            
            await db.commit()
            await db.refresh(question)
            return question

    @staticmethod
    async def delete(template_id: UUID, question_id: UUID) -> bool:
        async with async_session() as db:
            question = await QuestionService.get_by_id(template_id, question_id)
            if not question:
                return False
            
            await db.delete(question)
            await db.commit()
            return True
