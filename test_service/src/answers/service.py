from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from typing import List, Optional
from uuid import UUID
from fastapi import HTTPException, status

from src.answers.models import AnswerOption
from src.answers.schemas import AnswerOptionCreate, AnswerOptionRead
from src.questions.models import Question


class AnswerOptionService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_answer_option(self, data: AnswerOptionCreate) -> AnswerOptionRead:
        try:
            question_result = await self.db.execute(
                select(Question).where(Question.id == data.question_id)
            )
            question = question_result.scalar_one_or_none()
            if not question:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Question with id {data.question_id} not found",
                )

            new_item = AnswerOption(**data.model_dump(exclude_unset=True))
            self.db.add(new_item)
            await self.db.commit()
            await self.db.refresh(new_item)
            return AnswerOptionRead.model_validate(new_item)
        except IntegrityError as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to create answer option: {str(e)}",
            )
        except SQLAlchemyError as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}",
            )

    async def get_answer_option(self, answer_id: UUID) -> Optional[AnswerOptionRead]:
        try:
            result = await self.db.execute(
                select(AnswerOption).where(AnswerOption.id == answer_id)
            )
            obj = result.scalar_one_or_none()
            if not obj:
                return None
            return AnswerOptionRead.model_validate(obj)
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}",
            )

    async def list_answer_options(
        self, question_id: UUID, limit: int = 10, offset: int = 0
    ) -> List[AnswerOptionRead]:
        try:
            result = await self.db.execute(
                select(AnswerOption)
                .where(AnswerOption.question_id == question_id)
                .limit(limit)
                .offset(offset)
            )
            items = result.scalars().all()
            return [AnswerOptionRead.model_validate(item) for item in items]
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}",
            )

    async def delete_answer_option(self, answer_id: UUID) -> bool:
        try:
            result = await self.db.execute(
                select(AnswerOption).where(AnswerOption.id == answer_id)
            )
            obj = result.scalar_one_or_none()
            if not obj:
                return False
            await self.db.delete(obj)
            await self.db.commit()
            return True
        except SQLAlchemyError as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}",
            )
