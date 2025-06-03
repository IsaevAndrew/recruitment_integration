from fastapi import APIRouter, Depends, HTTPException, status, Query, \
    BackgroundTasks
from typing import List
from uuid import UUID
import httpx

from src.applications.dependencies import get_application_service
from src.applications.schemas import ApplicationRead
from src.applications.service import ApplicationService
from src.candidates.schemas import CandidateCreate, CandidateRead
from src.candidates.dependencies import get_candidate_service, \
    valid_candidate_id
from src.candidates.service import CandidateService
from src.config import settings

router = APIRouter(prefix="/candidates", tags=["candidates"])


@router.post("/", response_model=CandidateRead,
             status_code=status.HTTP_201_CREATED)
async def create_candidate(
        data: CandidateCreate,
        service: CandidateService = Depends(get_candidate_service),
):
    return await service.create_candidate(data)


@router.get("/{candidate_id}", response_model=CandidateRead)
async def read_candidate(
        candidate: dict = Depends(valid_candidate_id),
):
    return candidate


@router.get("/", response_model=List[CandidateRead])
async def list_candidates(
        limit: int = Query(default=10, ge=1),
        offset: int = Query(default=0, ge=0),
        service: CandidateService = Depends(get_candidate_service),
):
    return await service.list_candidates(limit=limit, offset=offset)


@router.put("/{candidate_id}", response_model=CandidateRead)
async def update_candidate(
        candidate_id: UUID,
        data: CandidateCreate,
        service: CandidateService = Depends(get_candidate_service),
):
    updated = await service.update_candidate(candidate_id, data)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Candidate not found"
        )
    return updated


@router.delete("/{candidate_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_candidate(
        candidate_id: UUID,
        service: CandidateService = Depends(get_candidate_service),
):
    deleted = await service.deactivate_candidate(candidate_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Candidate not found"
        )
    return None
