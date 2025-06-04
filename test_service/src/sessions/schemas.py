from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime


class SessionCreate(BaseModel):
    application_id: UUID
    template_id: UUID
    candidate_email: str


class SessionRead(BaseModel):
    id: UUID
    application_id: UUID
    template_id: UUID
    candidate_email: str
    created_at: Optional[datetime]
    score: Optional[int]

    model_config = {
        "from_attributes": True,
        "json_encoders": {datetime: lambda v: v.isoformat()},
    }


class SessionAnswerCreate(BaseModel):
    session_id: UUID
    question_id: UUID
    answer_id: UUID


class SessionAnswerRead(BaseModel):
    id: UUID
    session_id: UUID
    question_id: UUID
    answer_id: UUID
    created_at: Optional[datetime]

    model_config = {
        "from_attributes": True,
        "json_encoders": {datetime: lambda v: v.isoformat()},
    }
