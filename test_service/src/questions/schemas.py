from pydantic import BaseModel, Field
from datetime import datetime

from uuid import UUID


class QuestionBase(BaseModel):
    template_id: UUID
    text: str = Field(min_length=1)


class QuestionCreate(QuestionBase):
    pass


class QuestionRead(QuestionBase):
    id: UUID
    created_at: datetime

    model_config = {"from_attributes": True}
