from pydantic import BaseModel, ConfigDict, EmailStr
from datetime import datetime
from uuid import UUID
from enum import Enum
from typing import Optional, Literal

class UserRole(str, Enum):
    user = "user"
    moderator = "moderator"
    admin = "admin"

class UserOut(BaseModel):
    id: UUID
    name: Optional[str] = None
    username: str
    email: EmailStr
    type: UserRole
    img_link: str | None
    phone: Optional[str]
    birthdate: Optional[datetime]
    description: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class UserSearchRequest(BaseModel):
    search: Optional[str] = None
    role: Optional[str] = None
    reg_date_from: Optional[datetime] = None
    reg_date_to: Optional[datetime] = None
    sort_by: Literal["name", "registration_date"] = "name"
    sort_order: Literal["asc", "desc"] = "asc"