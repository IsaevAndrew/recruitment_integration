import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from typing import List, Optional
from uuid import UUID
from fastapi import HTTPException, status

from src.sessions.models import TestSession, SessionAnswer
from src.sessions.schemas import (
    SessionCreate,
    SessionRead,
    SessionAnswerCreate,
    SessionAnswerRead,
)
from src.config import settings
from src.answers.models import AnswerOption
from src.templates.models import TestTemplate
from src.questions.models import Question


class SessionService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_session(self, data: SessionCreate) -> SessionRead:
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

            new_item = TestSession(
                application_id=data.application_id,
                template_id=data.template_id,
                candidate_email=data.candidate_email,
            )
            self.db.add(new_item)
            await self.db.commit()
            await self.db.refresh(new_item)
            return SessionRead.model_validate(new_item)
        except IntegrityError as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to create session: {str(e)}",
            )
        except SQLAlchemyError as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}",
            )

    async def get_session(self, session_id: UUID) -> Optional[SessionRead]:
        try:
            result = await self.db.execute(
                select(TestSession).where(TestSession.id == session_id)
            )
            obj = result.scalar_one_or_none()
            if not obj:
                return None
            return SessionRead.model_validate(obj)
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}",
            )

    async def list_sessions(
        self, limit: int = 10, offset: int = 0
    ) -> List[SessionRead]:
        try:
            result = await self.db.execute(
                select(TestSession).limit(limit).offset(offset)
            )
            items = result.scalars().all()
            return [SessionRead.model_validate(item) for item in items]
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}",
            )

    async def create_answer(self, data: SessionAnswerCreate) -> SessionAnswerRead:
        try:
            # Check if session exists
            session_result = await self.db.execute(
                select(TestSession).where(TestSession.id == data.session_id)
            )
            session = session_result.scalar_one_or_none()
            if not session:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Session with id {data.session_id} not found",
                )

            # Check if question exists and belongs to the session's template
            question_result = await self.db.execute(
                select(Question)
                .where(Question.id == data.question_id)
                .where(Question.template_id == session.template_id)
            )
            question = question_result.scalar_one_or_none()
            if not question:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Question with id {data.question_id} not found or does not belong to the session's template",
                )

            # Check if answer option exists and belongs to the question
            answer_result = await self.db.execute(
                select(AnswerOption)
                .where(AnswerOption.id == data.answer_id)
                .where(AnswerOption.question_id == data.question_id)
            )
            answer = answer_result.scalar_one_or_none()
            if not answer:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Answer option with id {data.answer_id} not found or does not belong to the question",
                )

            new_item = SessionAnswer(**data.model_dump(exclude_unset=True))
            self.db.add(new_item)
            await self.db.commit()
            await self.db.refresh(new_item)
            return SessionAnswerRead.model_validate(new_item)
        except IntegrityError as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to create answer: {str(e)}",
            )
        except SQLAlchemyError as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}",
            )

    async def list_answers_for_session(
        self, session_id: UUID, limit: int = 10, offset: int = 0
    ) -> List[SessionAnswerRead]:
        try:
            result = await self.db.execute(
                select(SessionAnswer)
                .where(SessionAnswer.session_id == session_id)
                .limit(limit)
                .offset(offset)
            )
            items = result.scalars().all()
            return [SessionAnswerRead.model_validate(item) for item in items]
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}",
            )

    async def calculate_score_and_callback(self, session_id: UUID) -> None:
        try:
            result = await self.db.execute(
                select(TestSession).where(TestSession.id == session_id)
            )
            session_obj = result.scalar_one_or_none()
            if not session_obj:
                return

            result_all = await self.db.execute(
                select(SessionAnswer).where(SessionAnswer.session_id == session_id)
            )
            all_answers = result_all.scalars().all()

            correct_count = 0
            for ans in all_answers:
                ans_res = await self.db.execute(
                    select(AnswerOption).where(AnswerOption.id == ans.answer_id)
                )
                answer_option = ans_res.scalar_one_or_none()
                if answer_option and answer_option.correct:
                    correct_count += 1

            session_obj.score = correct_count
            await self.db.commit()
            await self.db.refresh(session_obj)

            callback_payload = {"session_id": str(session_id), "score": correct_count}
            async with httpx.AsyncClient() as client:
                try:
                    await client.post(
                        f"{settings.CANDIDATE_SERVICE_URL}/applications/{session_obj.application_id}/test-result",
                        json=callback_payload,
                        timeout=10.0,
                    )
                except httpx.RequestError as e:
                    # Log the error but don't fail the operation
                    print(f"Failed to send callback: {str(e)}")
        except SQLAlchemyError as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}",
            )

    async def finish_session(self, session_id: UUID) -> Optional[SessionRead]:
        try:
            await self.calculate_score_and_callback(session_id)
            return await self.get_session(session_id)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to finish session: {str(e)}",
            )
