from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from uuid import UUID


class AnswerBase(BaseModel):
    question_id: UUID
    text: str = Field(min_length=1)
    correct: bool = Field(default=False)


class AnswerCreate(AnswerBase):
    pass


class AnswerRead(AnswerBase):
    id: UUID
    created_at: datetime

    model_config = {"from_attributes": True}
