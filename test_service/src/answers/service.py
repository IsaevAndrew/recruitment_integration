from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from uuid import UUID

from src.answers.models import AnswerOption
from src.answers.schemas import AnswerOptionCreate, AnswerOptionRead


class AnswerOptionService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_answer_option(self, data: AnswerOptionCreate) -> AnswerOptionRead:
        new_item = AnswerOption(**data.model_dump(exclude_unset=True))
        self.db.add(new_item)
        await self.db.commit()
        await self.db.refresh(new_item)
        return AnswerOptionRead.model_validate(new_item)

    async def get_answer_option(self, answer_id: UUID) -> Optional[AnswerOptionRead]:
        result = await self.db.execute(
            select(AnswerOption).where(AnswerOption.id == answer_id)
        )
        obj = result.scalar_one_or_none()
        if not obj:
            return None
        return AnswerOptionRead.model_validate(obj)

    async def list_answer_options(
        self, question_id: UUID, limit: int = 10, offset: int = 0
    ) -> List[AnswerOptionRead]:
        result = await self.db.execute(
            select(AnswerOption)
            .where(AnswerOption.question_id == question_id)
            .limit(limit)
            .offset(offset)
        )
        items = result.scalars().all()
        return [AnswerOptionRead.model_validate(item) for item in items]

    async def delete_answer_option(self, answer_id: UUID) -> bool:
        result = await self.db.execute(
            select(AnswerOption).where(AnswerOption.id == answer_id)
        )
        obj = result.scalar_one_or_none()
        if not obj:
            return False
        await self.db.delete(obj)
        await self.db.commit()
        return True
