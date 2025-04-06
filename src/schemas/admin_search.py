from pydantic import BaseModel
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
    name: str
    email: str
    type: UserRole
    img_link: str | None
    created_at: datetime

    class Config:
        orm_mode = True

class UserSearchRequest(BaseModel):
    search: Optional[str] = None
    role: Optional[str] = None
    reg_date_from: Optional[datetime] = None
    reg_date_to: Optional[datetime] = None
    sort_by: Literal["name", "registration_date"] = "name"
    sort_order: Literal["asc", "desc"] = "asc"