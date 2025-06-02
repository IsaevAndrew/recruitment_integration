from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import async_session
from src.answers.models import AnswerOption
from src.answers.schemas import AnswerOptionCreate, AnswerOptionUpdate, AnswerOptionRead

class AnswerService:
    @staticmethod
    async def create(question_id: UUID, data: AnswerOptionCreate) -> AnswerOptionRead:
        async with async_session() as db:
            answer = AnswerOption(**data.model_dump())
            db.add(answer)
            await db.commit()
            await db.refresh(answer)
            return answer

    @staticmethod
    async def get_all(question_id: UUID, skip: int = 0, limit: int = 100) -> List[AnswerOptionRead]:
        async with async_session() as db:
            result = await db.execute(
                select(AnswerOption)
                .where(AnswerOption.question_id == question_id)
                .offset(skip)
                .limit(limit)
            )
            return result.scalars().all()

    @staticmethod
    async def get_by_id(question_id: UUID, answer_id: UUID) -> Optional[AnswerOptionRead]:
        async with async_session() as db:
            result = await db.execute(
                select(AnswerOption)
                .where(AnswerOption.question_id == question_id)
                .where(AnswerOption.id == answer_id)
            )
            return result.scalar_one_or_none()

    @staticmethod
    async def update(question_id: UUID, answer_id: UUID, data: AnswerOptionUpdate) -> Optional[AnswerOptionRead]:
        async with async_session() as db:
            answer = await AnswerService.get_by_id(question_id, answer_id)
            if not answer:
                return None
            
            update_data = data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(answer, field, value)
            
            await db.commit()
            await db.refresh(answer)
            return answer

    @staticmethod
    async def delete(question_id: UUID, answer_id: UUID) -> bool:
        async with async_session() as db:
            answer = await AnswerService.get_by_id(question_id, answer_id)
            if not answer:
                return False
            
            await db.delete(answer)
            await db.commit()
            return True
