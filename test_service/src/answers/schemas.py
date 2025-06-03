from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from uuid import UUID


class AnswerOptionBase(BaseModel):
    question_id: UUID
    text: str
    correct: bool = False


class AnswerOptionCreate(AnswerOptionBase):
    pass


class AnswerOptionRead(AnswerOptionBase):
    id: UUID
    created_at: datetime

    model_config = {"from_attributes": True}
