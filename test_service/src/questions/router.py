from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List
from uuid import UUID

from src.questions.schemas import QuestionCreate, QuestionRead
from src.questions.dependencies import get_question_service, valid_question_id
from src.questions.service import QuestionService

router = APIRouter()


@router.post("/", response_model=QuestionRead, status_code=status.HTTP_201_CREATED)
async def create_question(
    data: QuestionCreate,
    service: QuestionService = Depends(get_question_service),
):
    return await service.create_question(data)


@router.get("/{question_id}", response_model=QuestionRead)
async def read_question(
    question: dict = Depends(valid_question_id),
):
    return question


@router.get("/", response_model=List[QuestionRead])
async def list_questions(
    template_id: UUID,
    limit: int = Query(default=10, ge=1),
    offset: int = Query(default=0, ge=0),
    service: QuestionService = Depends(get_question_service),
):
    return await service.list_questions(
        template_id=template_id, limit=limit, offset=offset
    )
