from pydantic import BaseModel, EmailStr
from datetime import date
from typing import Optional
from uuid import UUID


class UserLogin(BaseModel):
    username: str
    password: str

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    name: str
    
    phone: Optional[str] = None
    birthdate: Optional[date] = None
    description: Optional[str] = None
    img_link: Optional[str] = None

class UserResponse(BaseModel):
    id: UUID
    username: str
    email: str
    type: str
    name: Optional[str]
    phone: Optional[str]
    birthdate: Optional[date]
    description: Optional[str]
    img_link: Optional[str]
    is_active: bool

    class Config:
        from_attributes = True


class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

