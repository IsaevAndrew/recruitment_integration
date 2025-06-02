from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime

class TestTemplateBase(BaseModel):
    title: str
    description: Optional[str] = None

class TestTemplateCreate(TestTemplateBase):
    pass

class TestTemplateUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None

class TestTemplateRead(TestTemplateBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
