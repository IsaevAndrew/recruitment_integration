from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.candidates.schemas import CandidateCreate, CandidateUpdate, \
    CandidateRead
from src.candidates.models import Candidate
from src.database import async_session
from src.utils import hash_password


class CandidateService:
    @staticmethod
    async def create(data: CandidateCreate) -> CandidateRead:
        async with async_session() as session:
            stmt = select(Candidate).where(Candidate.email == data.email)
            existing = await session.execute(stmt)
            if existing.scalar_one_or_none():
                raise Exception("Email already registered")

            hashed_pw = hash_password(data.password)
            db_obj = Candidate(
                last_name=data.last_name,
                first_name=data.first_name,
                middle_name=data.middle_name,
                email=data.email,
                phone=data.phone,
                password_hash=hashed_pw,
                status="new",
            )
            session.add(db_obj)
            await session.commit()
            await session.refresh(db_obj)
            return CandidateRead.from_orm(db_obj)

    @staticmethod
    async def get_all(skip: int = 0, limit: int = 100) -> List[CandidateRead]:
        async with async_session() as session:
            stmt = select(Candidate).offset(skip).limit(limit)
            result = await session.execute(stmt)
            candidates = result.scalars().all()
            return [CandidateRead.from_orm(obj) for obj in candidates]

    @staticmethod
    async def get_by_id(candidate_id: int) -> Optional[CandidateRead]:
        async with async_session() as session:
            stmt = select(Candidate).where(Candidate.id == candidate_id)
            result = await session.execute(stmt)
            obj = result.scalar_one_or_none()
            if not obj:
                return None
            return CandidateRead.from_orm(obj)

    @staticmethod
    async def update(candidate_id: int, data: CandidateUpdate) -> Optional[
        CandidateRead]:

        async with async_session() as session:
            stmt = select(Candidate).where(Candidate.id == candidate_id)
            result = await session.execute(stmt)
            obj: Candidate = result.scalar_one_or_none()
            if not obj:
                return None

            update_data = data.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(obj, field, value)
            session.add(obj)
            await session.commit()
            await session.refresh(obj)
            return CandidateRead.from_orm(obj)

    @staticmethod
    async def delete(candidate_id: int) -> bool:
        async with async_session() as session:
            stmt = select(Candidate).where(Candidate.id == candidate_id)
            result = await session.execute(stmt)
            obj: Candidate = result.scalar_one_or_none()
            if not obj:
                return False
            await session.delete(obj)
            await session.commit()
            return True
