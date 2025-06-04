from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from typing import List, Optional
from uuid import UUID
from fastapi import HTTPException, status

from src.questions.models import Question
from src.questions.schemas import QuestionCreate, QuestionRead
from src.templates.models import TestTemplate


class QuestionService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_question(self, data: QuestionCreate) -> QuestionRead:
        try:
            # Check if template exists
            template_result = await self.db.execute(
                select(TestTemplate).where(TestTemplate.id == data.template_id)
            )
            template = template_result.scalar_one_or_none()
            if not template:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Template with id {data.template_id} not found",
                )

            new_item = Question(**data.model_dump(exclude_unset=True))
            self.db.add(new_item)
            await self.db.commit()
            await self.db.refresh(new_item)
            return QuestionRead.model_validate(new_item)
        except IntegrityError as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to create question: {str(e)}",
            )
        except SQLAlchemyError as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}",
            )

    async def get_question(self, question_id: UUID) -> Optional[QuestionRead]:
        try:
            result = await self.db.execute(
                select(Question).where(Question.id == question_id)
            )
            obj = result.scalar_one_or_none()
            if not obj:
                return None
            return QuestionRead.model_validate(obj)
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}",
            )

    async def list_questions(
        self, template_id: UUID, limit: int = 10, offset: int = 0
    ) -> List[QuestionRead]:
        try:
            result = await self.db.execute(
                select(Question)
                .where(Question.template_id == template_id)
                .limit(limit)
                .offset(offset)
            )
            items = result.scalars().all()
            return [QuestionRead.model_validate(item) for item in items]
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}",
            )

    async def update_question(
        self, question_id: UUID, data: QuestionCreate
    ) -> Optional[QuestionRead]:
        try:
            result = await self.db.execute(
                select(Question).where(Question.id == question_id)
            )
            obj = result.scalar_one_or_none()
            if not obj:
                return None
            for field, value in data.model_dump(exclude_unset=True).items():
                setattr(obj, field, value)
            await self.db.commit()
            await self.db.refresh(obj)
            return QuestionRead.model_validate(obj)
        except IntegrityError as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to update question: {str(e)}",
            )
        except SQLAlchemyError as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}",
            )

    async def delete_question(self, question_id: UUID) -> bool:
        try:
            result = await self.db.execute(
                select(Question).where(Question.id == question_id)
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
