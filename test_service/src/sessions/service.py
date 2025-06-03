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


class SessionService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_session(self, data: SessionCreate) -> SessionRead:
        new_item = TestSession(**data.model_dump(exclude_unset=True))
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
        self, candidate_email: str, limit: int = 10, offset: int = 0
    ) -> List[SessionRead]:
        result = await self.db.execute(
            select(TestSession)
            .where(TestSession.candidate_email == candidate_email)
            .limit(limit)
            .offset(offset)
        )
        items = result.scalars().all()
        return [SessionRead.model_validate(item) for item in items]

    async def update_score(self, session_id: UUID, score: int) -> Optional[SessionRead]:
        result = await self.db.execute(
            select(TestSession).where(TestSession.id == session_id)
        )
        obj = result.scalar_one_or_none()
        if not obj:
            return None
        obj.score = score
        await self.db.commit()
        await self.db.refresh(obj)
        return SessionRead.model_validate(obj)

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
