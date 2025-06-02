from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import Optional, List
from uuid import UUID


class SessionBase(BaseModel):
    template_id: UUID
    candidate_email: EmailStr


class SessionCreate(SessionBase):
    pass


class SessionRead(SessionBase):
    id: UUID
    score: Optional[int]
    created_at: datetime

    model_config = {"from_attributes": True}


class SessionAnswerBase(BaseModel):
    session_id: UUID
    question_id: UUID
    answer_id: UUID


class SessionAnswerCreate(SessionAnswerBase):
    pass


class SessionAnswerRead(SessionAnswerBase):
    id: UUID
    created_at: datetime

    model_config = {"from_attributes": True}
