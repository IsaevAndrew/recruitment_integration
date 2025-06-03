from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List
from uuid import UUID

from src.sessions.schemas import (
    SessionCreate,
    SessionRead,
    SessionAnswerCreate,
    SessionAnswerRead,
)
from src.sessions.dependencies import get_session_service, valid_session_id
from src.sessions.service import SessionService

router = APIRouter()


@router.post("/", response_model=SessionRead, status_code=status.HTTP_201_CREATED)
async def create_session(
    data: SessionCreate,
    service: SessionService = Depends(get_session_service),
):
    return await service.create_session(data)


@router.get("/{session_id}", response_model=SessionRead)
async def read_session(session: dict = Depends(valid_session_id)):
    return session


@router.get("/", response_model=List[SessionRead])
async def list_sessions(
    candidate_email: str,
    limit: int = Query(default=10, ge=1),
    offset: int = Query(default=0, ge=0),
    service: SessionService = Depends(get_session_service),
):
    return await service.list_sessions(
        candidate_email=candidate_email, limit=limit, offset=offset
    )


@router.patch("/{session_id}/score", response_model=SessionRead)
async def update_score(
    session_id: UUID,
    score: int = Query(..., ge=0, le=100),
    service: SessionService = Depends(get_session_service),
):
    updated = await service.update_score(session_id, score)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
        )
    return updated


@router.post(
    "/answers", response_model=SessionAnswerRead, status_code=status.HTTP_201_CREATED
)
async def create_session_answer(
    data: SessionAnswerCreate,
    service: SessionService = Depends(get_session_service),
):
    return await service.create_answer(data)


@router.get("/{session_id}/answers", response_model=List[SessionAnswerRead])
async def list_session_answers(
    session_id: UUID,
    limit: int = Query(default=10, ge=1),
    offset: int = Query(default=0, ge=0),
    service: SessionService = Depends(get_session_service),
):
    return await service.list_answers_for_session(
        session_id=session_id, limit=limit, offset=offset
    )
