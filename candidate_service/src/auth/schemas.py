from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr
from uuid import UUID


class UserBase(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    role: str = Field(default="user", pattern="^(user|admin)$")


class UserCreate(UserBase):
    password: str = Field(min_length=8)
    email: EmailStr


class UserRead(UserBase):
    id: UUID
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class LoginRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: str
    role: str
    exp: Optional[datetime] = None
