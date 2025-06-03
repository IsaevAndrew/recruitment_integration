from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List
from uuid import UUID

from src.answers.schemas import AnswerCreate, AnswerRead
from src.answers.dependencies import get_answer_service, valid_answer_id
from src.answers.service import AnswerService

router = APIRouter()


@router.post("/", response_model=AnswerRead, status_code=status.HTTP_201_CREATED)
async def create_answer(
    data: AnswerCreate,
    service: AnswerService = Depends(get_answer_service),
):
    return await service.create_answer(data)


@router.get("/{answer_id}", response_model=AnswerRead)
async def read_answer(answer: dict = Depends(valid_answer_id)):
    return answer


@router.get("/", response_model=List[AnswerRead])
async def list_answers(
    question_id: UUID,
    limit: int = Query(default=10, ge=1),
    offset: int = Query(default=0, ge=0),
    service: AnswerService = Depends(get_answer_service),
):
    return await service.list_answers(
        question_id=question_id, limit=limit, offset=offset
    )
