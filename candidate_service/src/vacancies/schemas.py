from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class VacancyBase(BaseModel):
    title: str
    description: Optional[str] = None


class VacancyCreate(VacancyBase):
    pass


class VacancyRead(VacancyBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


class VacancyUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
