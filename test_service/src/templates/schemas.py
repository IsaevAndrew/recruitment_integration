from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from uuid import UUID


class TemplateBase(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    description: Optional[str] = None


class TemplateCreate(TemplateBase):
    pass


class TemplateRead(TemplateBase):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = {"from_attributes": True}
