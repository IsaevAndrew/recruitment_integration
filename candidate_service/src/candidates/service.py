from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from uuid import UUID
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from fastapi import HTTPException, status

from src.candidates.models import Candidate
from src.candidates.schemas import CandidateCreate, CandidateRead


class CandidateService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_candidate(self, data: CandidateCreate) -> CandidateRead:
        try:
            existing_candidate = await self.db.execute(
                select(Candidate).where(Candidate.email == data.email)
            )
            if existing_candidate.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Candidate with email {data.email} already exists",
                )

            new_item = Candidate(**data.model_dump(exclude_unset=True))
            self.db.add(new_item)
            await self.db.commit()
            await self.db.refresh(new_item)
            return CandidateRead.model_validate(new_item)
        except IntegrityError as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to create candidate: {str(e)}",
            )
        except SQLAlchemyError as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}",
            )

    async def get_candidate(self, candidate_id: UUID) -> Optional[CandidateRead]:
        try:
            result = await self.db.execute(
                select(Candidate).where(Candidate.id == candidate_id)
            )
            obj = result.scalar_one_or_none()
            if not obj:
                return None
            return CandidateRead.model_validate(obj)
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}",
            )

    async def list_candidates(
        self, limit: int = 10, offset: int = 0
    ) -> List[CandidateRead]:
        try:
            result = await self.db.execute(
                select(Candidate).limit(limit).offset(offset)
            )
            items = result.scalars().all()
            return [CandidateRead.model_validate(item) for item in items]
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}",
            )

    async def update_candidate(
        self, candidate_id: UUID, data: CandidateCreate
    ) -> Optional[CandidateRead]:
        try:
            result = await self.db.execute(
                select(Candidate).where(Candidate.id == candidate_id)
            )
            obj = result.scalar_one_or_none()
            if not obj:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Candidate with id {candidate_id} not found",
                )

            if data.email != obj.email:
                existing_candidate = await self.db.execute(
                    select(Candidate).where(Candidate.email == data.email)
                )
                if existing_candidate.scalar_one_or_none():
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Candidate with email {data.email} already exists",
                    )

            for field, value in data.model_dump(exclude_unset=True).items():
                setattr(obj, field, value)
            await self.db.commit()
            await self.db.refresh(obj)
            return CandidateRead.model_validate(obj)
        except IntegrityError as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to update candidate: {str(e)}",
            )
        except SQLAlchemyError as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}",
            )

    async def deactivate_candidate(self, candidate_id: UUID) -> Optional[CandidateRead]:
        try:
            result = await self.db.execute(
                select(Candidate).where(Candidate.id == candidate_id)
            )
            obj = result.scalar_one_or_none()
            if not obj:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Candidate with id {candidate_id} not found",
                )

            obj.is_active = False
            await self.db.commit()
            await self.db.refresh(obj)
            return CandidateRead.model_validate(obj)
        except SQLAlchemyError as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}",
            )
