from pydantic import BaseModel
from uuid import UUID
from typing import List, Dict, Optional, Literal
from datetime import datetime

class PostSearchRequest(BaseModel):
    keyword: Optional[str] = None
    tags: Optional[str] = None
    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None
    sort_by: Literal["date", "rating"] = "date"
    order: Literal["asc", "desc"] = "desc"
    rating_to: Optional[float] = None


class UserSearchResponse(BaseModel):
    id: UUID
    img_link: Optional[str]
    name: Optional[str]

    class Config:
        from_attributes = True

class TagResponse(BaseModel):
    name: Optional[str] = None

    class Config:
        from_attributes = True

class PostResponse(BaseModel):
    id: UUID
    title: str
    description: str
    image_url: str
    location: Optional[str] = None
    user: Optional[UserSearchResponse] = None
    created_at: datetime
    tags: List[TagResponse] = []
    avg_rating: Optional[float] = None
    rating_count: Optional[int] = None

    class Config:
        from_attributes = True