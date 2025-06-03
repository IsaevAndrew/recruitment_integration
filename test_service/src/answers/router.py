from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List
from uuid import UUID

from src.answers.schemas import AnswerOptionCreate, AnswerOptionRead
from src.answers.dependencies import get_answer_service, valid_answer_id
from src.answers.service import AnswerOptionService

router = APIRouter(prefix="/answers", tags=["answers"])


@router.post("/", response_model=AnswerOptionRead, status_code=status.HTTP_201_CREATED)
async def create_answer_option(
    data: AnswerOptionCreate,
    service: AnswerOptionService = Depends(get_answer_service),
):
    return await service.create_answer_option(data)


@router.get("/{answer_id}", response_model=AnswerOptionRead)
async def read_answer_option(
    answer: dict = Depends(valid_answer_id),
):
    return answer


@router.get("/", response_model=List[AnswerOptionRead])
async def list_answer_options(
    question_id: UUID,
    limit: int = Query(default=10, ge=1),
    offset: int = Query(default=0, ge=0),
    service: AnswerOptionService = Depends(get_answer_service),
):
    return await service.list_answer_options(
        question_id=question_id, limit=limit, offset=offset
    )


@router.delete("/{answer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_answer_option(
    answer_id: UUID,
    service: AnswerOptionService = Depends(get_answer_service),
):
    deleted = await service.delete_answer_option(answer_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Answer not found"
        )
    return None
