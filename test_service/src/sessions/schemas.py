from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional, List

class TestSessionCreate(BaseModel):
    external_application_id: UUID

class TestSessionRead(BaseModel):
    id: UUID
    test_id: UUID
    external_application_id: UUID
    token: str
    status: str
    score: Optional[float]
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True

class SessionAnswerCreate(BaseModel):
    session_id: UUID
    question_id: UUID
    answer_id: UUID

class SessionAnswerRead(BaseModel):
    id: UUID
    session_id: UUID
    question_id: UUID
    answer_id: UUID
    answered_at: datetime

    class Config:
        from_attributes = True
