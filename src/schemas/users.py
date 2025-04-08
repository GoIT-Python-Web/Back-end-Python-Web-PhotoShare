from pydantic import BaseModel, EmailStr
from datetime import datetime
from uuid import UUID
from enum import Enum

class UserTypeEnum(str, Enum):
    user = "user"
    admin = "admin"

class MyselfOut(BaseModel):
    id: UUID
    username: str
    name: str | None
    email: EmailStr
    phone: str | None
    type: UserTypeEnum
    birthdate: datetime | None
    description: str | None
    img_link: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True