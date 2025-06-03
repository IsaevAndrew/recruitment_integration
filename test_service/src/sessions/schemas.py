from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID


class SessionCreate(BaseModel):
    application_id: UUID
    template_id: UUID
    candidate_email: str


class SessionRead(BaseModel):
    id: UUID
    application_id: UUID
    template_id: UUID
    candidate_email: str
    created_at: Optional[str]
    score: Optional[int]

    model_config = {"from_attributes": True}


class SessionAnswerCreate(BaseModel):
    session_id: UUID
    question_id: UUID
    answer_id: UUID


class SessionAnswerRead(BaseModel):
    id: UUID
    session_id: UUID
    question_id: UUID
    answer_id: UUID
    created_at: Optional[str]

    model_config = {"from_attributes": True}
