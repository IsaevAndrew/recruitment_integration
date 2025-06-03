from fastapi import HTTPException, status, Depends
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_db
from src.candidates.service import CandidateService


async def get_candidate_service(db: AsyncSession = Depends(get_db)) -> CandidateService:
    return CandidateService(db)


async def valid_candidate_id(
    candidate_id: UUID,
    service: CandidateService = Depends(get_candidate_service),
) -> dict:
    candidate = await service.get_candidate(candidate_id)
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Candidate not found"
        )
    return candidate
