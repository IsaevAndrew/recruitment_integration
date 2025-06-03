from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List
from uuid import UUID

from src.questions.schemas import QuestionCreate, QuestionRead
from src.questions.dependencies import get_question_service, valid_question_id
from src.questions.service import QuestionService

router = APIRouter(prefix="/questions", tags=["questions"])


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


@router.put("/{question_id}", response_model=QuestionRead)
async def update_question(
    question_id: UUID,
    data: QuestionCreate,
    service: QuestionService = Depends(get_question_service),
):
    updated = await service.update_question(question_id, data)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Question not found"
        )
    return updated


@router.delete("/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_question(
    question_id: UUID,
    service: QuestionService = Depends(get_question_service),
):
    deleted = await service.delete_question(question_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Question not found"
        )
    return None
