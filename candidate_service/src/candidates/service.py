from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from uuid import UUID

from src.candidates.models import Candidate
from src.candidates.schemas import CandidateCreate, CandidateRead


class CandidateService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_candidate(self, data: CandidateCreate) -> CandidateRead:
        new_item = Candidate(**data.model_dump(exclude_unset=True))
        self.db.add(new_item)
        await self.db.commit()
        await self.db.refresh(new_item)
        return CandidateRead.model_validate(new_item)

    async def get_candidate(self, candidate_id: UUID) -> Optional[CandidateRead]:
        result = await self.db.execute(
            select(Candidate).where(Candidate.id == candidate_id)
        )
        obj = result.scalar_one_or_none()
        if not obj:
            return None
        return CandidateRead.model_validate(obj)

    async def list_candidates(
        self, limit: int = 10, offset: int = 0
    ) -> List[CandidateRead]:
        result = await self.db.execute(select(Candidate).limit(limit).offset(offset))
        items = result.scalars().all()
        return [CandidateRead.model_validate(item) for item in items]

    async def update_candidate(
        self, candidate_id: UUID, data: CandidateCreate
    ) -> Optional[CandidateRead]:
        result = await self.db.execute(
            select(Candidate).where(Candidate.id == candidate_id)
        )
        obj = result.scalar_one_or_none()
        if not obj:
            return None
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(obj, field, value)
        await self.db.commit()
        await self.db.refresh(obj)
        return CandidateRead.model_validate(obj)

    async def deactivate_candidate(self, candidate_id: UUID) -> Optional[CandidateRead]:
        result = await self.db.execute(
            select(Candidate).where(Candidate.id == candidate_id)
        )
        obj = result.scalar_one_or_none()
        if not obj:
            return None
        obj.is_active = False
        await self.db.commit()
        await self.db.refresh(obj)
        return CandidateRead.model_validate(obj)
