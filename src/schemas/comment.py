from pydantic import BaseModel, UUID4
from datetime import datetime

class CommentCreateDTO(BaseModel):
    message: str

class CommentOut(BaseModel):
    id: UUID4
    user_id: UUID4
    post_id: UUID4
    message: str
    created_at: datetime

    class Config:
        orm_mode = True
