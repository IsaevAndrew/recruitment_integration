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

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("/", response_model=SessionRead, status_code=status.HTTP_201_CREATED)
async def create_session(
    data: SessionCreate,
    service: SessionService = Depends(get_session_service),
):
    """
    Создаём тестовую сессию: application_id, template_id, candidate_email.
    """
    new_session = await service.create_session(data)
    return new_session


@router.get("/{session_id}", response_model=SessionRead)
async def read_session(
    session: dict = Depends(valid_session_id),
):
    return session


@router.get("/", response_model=List[SessionRead])
async def list_sessions(
    limit: int = Query(default=10, ge=1),
    offset: int = Query(default=0, ge=0),
    service: SessionService = Depends(get_session_service),
):
    return await service.list_sessions(limit=limit, offset=offset)


@router.post(
    "/answers", response_model=SessionAnswerRead, status_code=status.HTTP_201_CREATED
)
async def create_answer(
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


@router.post("/{session_id}/finish", response_model=SessionRead)
async def finish_session(
    session_id: UUID,
    service: SessionService = Depends(get_session_service),
):
    """
    Завершить тестовую сессию: подсчитать score и вызвать callback в candidate_service.
    """
    updated = await service.finish_session(session_id)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
        )
    return updated
