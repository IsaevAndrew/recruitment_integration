import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from uuid import UUID

from src.sessions.models import TestSession, SessionAnswer
from src.sessions.schemas import (
    SessionCreate,
    SessionRead,
    SessionAnswerCreate,
    SessionAnswerRead,
)
from src.config import settings
from src.answers.models import AnswerOption


class SessionService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_session(self, data: SessionCreate) -> SessionRead:
        new_item = TestSession(
            application_id=data.application_id,
            template_id=data.template_id,
            candidate_email=data.candidate_email,
        )
        self.db.add(new_item)
        await self.db.commit()
        await self.db.refresh(new_item)
        return SessionRead.model_validate(new_item)

    async def get_session(self, session_id: UUID) -> Optional[SessionRead]:
        result = await self.db.execute(
            select(TestSession).where(TestSession.id == session_id)
        )
        obj = result.scalar_one_or_none()
        if not obj:
            return None
        return SessionRead.model_validate(obj)

    async def list_sessions(
        self, limit: int = 10, offset: int = 0
    ) -> List[SessionRead]:
        result = await self.db.execute(select(TestSession).limit(limit).offset(offset))
        items = result.scalars().all()
        return [SessionRead.model_validate(item) for item in items]

    async def create_answer(self, data: SessionAnswerCreate) -> SessionAnswerRead:
        new_item = SessionAnswer(**data.model_dump(exclude_unset=True))
        self.db.add(new_item)
        await self.db.commit()
        await self.db.refresh(new_item)
        return SessionAnswerRead.model_validate(new_item)

    async def list_answers_for_session(
        self, session_id: UUID, limit: int = 10, offset: int = 0
    ) -> List[SessionAnswerRead]:
        result = await self.db.execute(
            select(SessionAnswer)
            .where(SessionAnswer.session_id == session_id)
            .limit(limit)
            .offset(offset)
        )
        items = result.scalars().all()
        return [SessionAnswerRead.model_validate(item) for item in items]

    async def calculate_score_and_callback(self, session_id: UUID) -> None:
        """
        Вызывается при POST /sessions/{session_id}/finish:
        — считает количество правильных ответов,
        — сохраняет score,
        — делает callback в candidate_service.
        """
        result = await self.db.execute(
            select(TestSession).where(TestSession.id == session_id)
        )
        session_obj = result.scalar_one_or_none()
        if not session_obj:
            return

        # Собираем все ответы по этой сессии
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

        # Сохраняем score в таблице test_sessions
        session_obj.score = correct_count
        await self.db.commit()
        await self.db.refresh(session_obj)

        # Делаем callback в candidate_service
        callback_payload = {"session_id": str(session_id), "score": correct_count}
        async with httpx.AsyncClient() as client:
            try:
                await client.post(
                    f"{settings.CANDIDATE_SERVICE_URL}/applications/{session_obj.application_id}/test-result",
                    json=callback_payload,
                    timeout=10.0,
                )
            except httpx.RequestError:
                pass

    async def finish_session(self, session_id: UUID) -> Optional[SessionRead]:
        await self.calculate_score_and_callback(session_id)
        return await self.get_session(session_id)
