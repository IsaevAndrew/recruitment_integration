from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from uuid import UUID

from src.questions.models import Question
from src.questions.schemas import QuestionCreate, QuestionRead


class QuestionService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_question(self, data: QuestionCreate) -> QuestionRead:
        new_item = Question(**data.model_dump(exclude_unset=True))
        self.db.add(new_item)
        await self.db.commit()
        await self.db.refresh(new_item)
        return QuestionRead.model_validate(new_item)

    async def get_question(self, question_id: UUID) -> Optional[QuestionRead]:
        result = await self.db.execute(
            select(Question).where(Question.id == question_id))
        obj = result.scalar_one_or_none()
        if not obj:
            return None
        return QuestionRead.model_validate(obj)

    async def list_questions(
            self, template_id: UUID, limit: int = 10, offset: int = 0
    ) -> List[QuestionRead]:
        result = await self.db.execute(
            select(Question).where(Question.template_id == template_id)
            .limit(limit).offset(offset)
        )
        items = result.scalars().all()
        return [QuestionRead.model_validate(item) for item in items]
