from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from uuid import UUID


class ApplicationBase(BaseModel):
    candidate_id: UUID
    vacancy_id: UUID


class ApplicationCreate(ApplicationBase):
    pass


class ApplicationRead(ApplicationBase):
    id: UUID
    status: str
    test_session_id: Optional[UUID]
    test_score: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = {"from_attributes": True}


class TestResultPayload(BaseModel):
    session_id: UUID
    score: int
