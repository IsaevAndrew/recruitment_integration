from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from src.sessions.schemas import TestSessionCreate, TestSessionRead, SessionAnswerCreate, SessionAnswerRead
from src.sessions.service import SessionService

router = APIRouter(prefix="/templates/{template_id}/sessions", tags=["sessions"])

@router.post("/", response_model=TestSessionRead, status_code=status.HTTP_201_CREATED)
async def create_session(template_id: str, data: TestSessionCreate):
    return await SessionService.create(template_id, data)

@router.get("/", response_model=List[TestSessionRead])
async def list_sessions(template_id: str, skip: int = 0, limit: int = 100):
    return await SessionService.get_all(template_id, skip, limit)

@router.get("/{session_id}", response_model=TestSessionRead)
async def get_session(template_id: str, session_id: str):
    session = await SessionService.get_by_id(template_id, session_id)
    if not session:
        raise HTTPException(404, "Session not found")
    return session

@router.put("/{session_id}", response_model=TestSessionRead)
async def update_session(template_id: str, session_id: str, data: TestSessionRead):
    updated = await SessionService.update(template_id, session_id, data)
    if not updated:
        raise HTTPException(404, "Session not found")
    return updated

@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(template_id: str, session_id: str):
    success = await SessionService.delete(template_id, session_id)
    if not success:
        raise HTTPException(404, "Session not found")
    return None

@router.post("/{session_id}/answers", response_model=SessionAnswerRead, status_code=status.HTTP_201_CREATED)
async def create_session_answer(template_id: str, session_id: str, data: SessionAnswerCreate):
    return await SessionService.create_answer(template_id, session_id, data)

@router.get("/{session_id}/answers", response_model=List[SessionAnswerRead])
async def list_session_answers(template_id: str, session_id: str, skip: int = 0, limit: int = 100):
    return await SessionService.get_answers(template_id, session_id, skip, limit)