from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from enum import Enum
from typing import Optional, List

class UserTypeEnum(str, Enum):
    user = "user"
    admin = "admin"

class UserBase(BaseModel):
    id: UUID
    username: str
    name: Optional[str] = None
    email: str
    phone: Optional[str] = None
    type: UserTypeEnum
    birthdate: Optional[datetime] = None
    description: Optional[str] = None
    img_link: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
