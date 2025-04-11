from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from uuid import UUID


class UserResponseForAdminPage(BaseModel):
    id: UUID
    username: str
    email: EmailStr
    type: str
    name: Optional[str]
    phone: Optional[str]
    birthdate: Optional[datetime]
    description: Optional[str]
    img_link: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
