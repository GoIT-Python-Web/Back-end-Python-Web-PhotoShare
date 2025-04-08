from datetime import datetime
from pydantic import BaseModel
from pydantic.config import ConfigDict
from typing import Optional
from uuid import UUID

class PostModel(BaseModel):
    title: str
    description: Optional[str] = None
    image_url: str
    location: Optional[str] = None
    created_at: datetime = None
    updated_at: datetime = None

    model_config = ConfigDict(from_attributes=True)

class PostResponse(BaseModel):
    id: UUID
    title: str
    user_id: UUID
    description: Optional[str] = None
    image_url: str
    location: Optional[str] = None
    created_at: datetime = None
    updated_at: datetime = None

    model_config = ConfigDict(from_attributes=True)

class PostUpdateRequest(BaseModel):
    description: Optional[str] = None

class PostUpdateResponse(BaseModel):
    message: str

class PostDeleteResponse(BaseModel):
    message: str
