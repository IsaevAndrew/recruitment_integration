from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.questions.schemas import QuestionCreate, QuestionRead, QuestionUpdate
from src.questions.service import QuestionService

router = APIRouter(
    prefix="/templates/{template_id}/questions",
    tags=["questions"]
)

@router.post("/", response_model=QuestionRead, status_code=status.HTTP_201_CREATED)
async def create_question(
    template_id: str,
    data: QuestionCreate,
    db: AsyncSession = Depends(get_db)
):
    return await QuestionService.create(db, template_id, data)

@router.get("/", response_model=List[QuestionRead])
async def list_questions(
    template_id: str,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    return await QuestionService.get_all(db, template_id, skip, limit)

@router.get("/{question_id}", response_model=QuestionRead)
async def get_question(
    template_id: str,
    question_id: str,
    db: AsyncSession = Depends(get_db)
):
    question = await QuestionService.get_by_id(db, template_id, question_id)
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )
    return question

@router.put("/{question_id}", response_model=QuestionRead)
async def update_question(
    template_id: str,
    question_id: str,
    data: QuestionUpdate,
    db: AsyncSession = Depends(get_db)
):
    updated = await QuestionService.update(db, template_id, question_id, data)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )
    return updated

@router.delete("/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_question(
    template_id: str,
    question_id: str,
    db: AsyncSession = Depends(get_db)
):
    success = await QuestionService.delete(db, template_id, question_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )
    return None