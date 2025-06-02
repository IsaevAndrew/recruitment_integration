from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from src.answers.schemas import AnswerOptionRead

class QuestionBase(BaseModel):
    test_id: UUID
    sequence: int
    text: str

class QuestionCreate(QuestionBase):
    pass

class QuestionUpdate(BaseModel):
    sequence: Optional[int] = None
    text: Optional[str] = None

class QuestionRead(QuestionBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    answer_options: List[AnswerOptionRead] = []

    class Config:
        from_attributes = True
