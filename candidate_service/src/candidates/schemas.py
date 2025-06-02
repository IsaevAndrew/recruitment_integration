from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class CandidateBase(BaseModel):
    last_name: str
    first_name: str
    middle_name: Optional[str] = None
    email: EmailStr
    phone: Optional[str] = None


class CandidateCreate(CandidateBase):
    password: str


class CandidateRead(CandidateBase):
    id: int
    status: str
    created_at: datetime

    class Config:
        orm_mode = True


class CandidateUpdate(BaseModel):
    last_name: Optional[str] = None
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    phone: Optional[str] = None
    status: Optional[str] = None
