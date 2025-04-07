from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

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

    model_config = {
        "from_attributes": True 
    }

