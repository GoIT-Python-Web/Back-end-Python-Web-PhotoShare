from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from enum import Enum


class UserTypeEnum(str, Enum):
    user = "user"
    admin = "admin"


class UserShortDTO(BaseModel):
    id: UUID
    name: str | None
    img_link: str | None
    type: UserTypeEnum

    model_config = {
        "from_attributes": True
    }


class CommentCreateDTO(BaseModel):
    message: str


class CommentUpdateDTO(BaseModel):
    message: str


class CommentOut(BaseModel):
    id: UUID
    user_id: UUID
    post_id: UUID
    message: str
    is_deleted: bool
    created_at: datetime
    updated_at: datetime
    user: UserShortDTO

    model_config = {
        "from_attributes": True 
    }
