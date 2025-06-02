from typing import List

from fastapi import APIRouter, Depends, status
from src.candidates.schemas import CandidateCreate, CandidateRead, \
    CandidateUpdate
from src.candidates.service import CandidateService
from src.candidates.dependencies import get_candidate_or_404, authenticated_user

router = APIRouter(prefix="/candidates", tags=["candidates"])


@router.post("/", response_model=CandidateRead,
             status_code=status.HTTP_201_CREATED)
async def create_candidate(
        data: CandidateCreate,
        _: dict = Depends(authenticated_user)
):
    return await CandidateService.create(data)


@router.get("/", response_model=List[CandidateRead])
async def list_candidates(
        skip: int = 0,
        limit: int = 100,
        _: dict = Depends(authenticated_user)
):
    return await CandidateService.get_all(skip, limit)


@router.get("/{candidate_id}", response_model=CandidateRead)
async def get_candidate(
        candidate: CandidateRead = Depends(get_candidate_or_404),
        _: dict = Depends(authenticated_user)
):
    return candidate


@router.put("/{candidate_id}", response_model=CandidateRead)
async def update_candidate(
        candidate_data: CandidateUpdate,
        candidate: CandidateRead = Depends(get_candidate_or_404),
        _: dict = Depends(authenticated_user)
):
    return await CandidateService.update(candidate.id, candidate_data)


@router.delete("/{candidate_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_candidate(
        candidate: CandidateRead = Depends(get_candidate_or_404),
        _: dict = Depends(authenticated_user)
):
    await CandidateService.delete(candidate.id)
    return None
