from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class ApplicationBase(BaseModel):
    candidate_id: int = Field(gt=0)
    vacancy_id: int = Field(gt=0)

class ApplicationCreate(ApplicationBase):
    pass

class ApplicationUpdate(BaseModel):
    status: Optional[str] = Field(None, pattern="^(new|in_progress|completed|rejected)$")
    test_score: Optional[int] = Field(None, ge=0, le=100)

class ApplicationRead(ApplicationBase):
    id: int
    status: str
    test_session_id: Optional[str] = None
    test_score: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True
