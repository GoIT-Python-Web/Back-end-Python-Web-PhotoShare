from datetime import datetime
from pydantic import BaseModel
from pydantic.config import ConfigDict
from typing import List, Optional
from uuid import UUID

class PostModel(BaseModel):
    title: str
    description: Optional[str] = None
    image_url: str
    location: Optional[str] = None
    created_at: datetime = None
    updated_at: datetime = None

    model_config = ConfigDict(from_attributes=True)

class UserShortResponse(BaseModel):
    id: UUID
    name: Optional[str]
    img_link: Optional[str]

    model_config = ConfigDict(from_attributes=True)

class TagsShortResponse(BaseModel):
    name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class PostResponse(BaseModel):
    id: UUID
    title: str
    user_id: UUID
    description: Optional[str] = None
    image_url: str
    location: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    avg_rating: Optional[float] = None
    rating_count: Optional[int] = None
    user: Optional[UserShortResponse] = None
    tags: Optional[List[TagsShortResponse]] = None

    model_config = ConfigDict(from_attributes=True)

class PostUpdateRequest(BaseModel):
    description: Optional[str] = None

class PostUpdateResponse(BaseModel):
    message: str

class PostDeleteResponse(BaseModel):
    message: str
