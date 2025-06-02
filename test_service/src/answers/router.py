from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from src.answers.schemas import AnswerOptionCreate, AnswerOptionRead, AnswerOptionUpdate
from src.answers.service import AnswerService

router = APIRouter(prefix="/questions/{question_id}/answers", tags=["answers"])

@router.post("/", response_model=AnswerOptionRead, status_code=status.HTTP_201_CREATED)
async def create_answer(question_id: str, data: AnswerOptionCreate):
    return await AnswerService.create(question_id, data)

@router.get("/", response_model=List[AnswerOptionRead])
async def list_answers(question_id: str, skip: int = 0, limit: int = 100):
    return await AnswerService.get_all(question_id, skip, limit)

@router.get("/{answer_id}", response_model=AnswerOptionRead)
async def get_answer(question_id: str, answer_id: str):
    answer = await AnswerService.get_by_id(question_id, answer_id)
    if not answer:
        raise HTTPException(404, "Answer not found")
    return answer

@router.put("/{answer_id}", response_model=AnswerOptionRead)
async def update_answer(question_id: str, answer_id: str, data: AnswerOptionUpdate):
    updated = await AnswerService.update(question_id, answer_id, data)
    if not updated:
        raise HTTPException(404, "Answer not found")
    return updated

@router.delete("/{answer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_answer(question_id: str, answer_id: str):
    success = await AnswerService.delete(question_id, answer_id)
    if not success:
        raise HTTPException(404, "Answer not found")
    return None