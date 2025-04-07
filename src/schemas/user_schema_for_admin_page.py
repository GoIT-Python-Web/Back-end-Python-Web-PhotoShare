from pydantic import BaseModel, EmailStr
from datetime import date
from typing import Optional
from uuid import UUID


class UserResponseForAdminPage(BaseModel):
    id: UUID
    username: str
    email: EmailStr
    type: str
    name: Optional[str]
    phone: Optional[str]
    birthdate: Optional[date]
    description: Optional[str]
    img_link: Optional[str]
    is_active: bool

    class Config:
        from_attributes = True
