from fastapi import Depends, HTTPException, status
from src.candidates.service import CandidateService
from src.auth.dependencies import get_current_user


async def get_candidate_or_404(candidate_id: int) -> dict:
    candidate = await CandidateService.get_by_id(candidate_id)
    if not candidate:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Candidate not found")
    return candidate


def authenticated_user(token_data: dict = Depends(get_current_user)):
    return token_data
