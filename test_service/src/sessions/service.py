from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from src.database import async_session
from src.sessions.models import TestSession, SessionAnswer
from src.sessions.schemas import TestSessionCreate, TestSessionRead, \
    SessionAnswerCreate, SessionAnswerRead
import secrets


class SessionService:
    @staticmethod
    async def create(template_id: UUID,
                     data: TestSessionCreate) -> TestSessionRead:
        async with async_session() as db:
            token = secrets.token_urlsafe(32)
            session = TestSession(
                test_id=template_id,
                external_application_id=data.external_application_id,
                token=token,
                status="created"
            )
            db.add(session)
            await db.commit()
            await db.refresh(session)
            return session

    @staticmethod
    async def get_all(template_id: UUID, skip: int = 0, limit: int = 100) -> \
    List[TestSessionRead]:
        async with async_session() as db:
            result = await db.execute(
                select(TestSession)
                .where(TestSession.test_id == template_id)
                .offset(skip)
                .limit(limit)
            )
            return result.scalars().all()

    @staticmethod
    async def get_by_id(template_id: UUID, session_id: UUID) -> Optional[
        TestSessionRead]:
        async with async_session() as db:
            result = await db.execute(
                select(TestSession)
                .where(TestSession.test_id == template_id)
                .where(TestSession.id == session_id)
            )
            return result.scalar_one_or_none()

    @staticmethod
    async def get_by_token(token: str) -> Optional[TestSessionRead]:
        async with async_session() as db:
            result = await db.execute(
                select(TestSession).where(TestSession.token == token)
            )
            return result.scalar_one_or_none()

    @staticmethod
    async def update(template_id: UUID, session_id: UUID,
                     data: TestSessionRead) -> Optional[TestSessionRead]:
        async with async_session() as db:
            session = await SessionService.get_by_id(template_id, session_id)
            if not session:
                return None

            update_data = data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(session, field, value)

            await db.commit()
            await db.refresh(session)
            return session

    @staticmethod
    async def delete(template_id: UUID, session_id: UUID) -> bool:
        async with async_session() as db:
            session = await SessionService.get_by_id(template_id, session_id)
            if not session:
                return False

            await db.delete(session)
            await db.commit()
            return True

    @staticmethod
    async def create_answer(template_id: UUID, session_id: UUID,
                            data: SessionAnswerCreate) -> SessionAnswerRead:
        async with async_session() as db:
            session = await SessionService.get_by_id(template_id, session_id)
            if not session:
                raise ValueError("Session not found")
            answer = SessionAnswer(**data.model_dump())
            db.add(answer)
            await db.commit()
            await db.refresh(answer)
            return answer

    @staticmethod
    async def get_answers(template_id: UUID, session_id: UUID, skip: int = 0,
                          limit: int = 100) -> List[SessionAnswerRead]:
        async with async_session() as db:
            session = await SessionService.get_by_id(template_id, session_id)
            if not session:
                raise ValueError("Session not found")
            result = await db.execute(
                select(SessionAnswer)
                .where(SessionAnswer.session_id == session_id)
                .offset(skip)
                .limit(limit)
            )
            return result.scalars().all()
