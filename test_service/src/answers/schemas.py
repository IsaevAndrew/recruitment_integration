from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional

class AnswerOptionBase(BaseModel):
    question_id: UUID
    sequence: int
    text: str
    is_correct: bool

class AnswerOptionCreate(AnswerOptionBase):
    pass

class AnswerOptionUpdate(BaseModel):
    sequence: Optional[int] = None
    text: Optional[str] = None
    is_correct: Optional[bool] = None

class AnswerOptionRead(AnswerOptionBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
