from pydantic import BaseModel, UUID4
from typing import List, Optional


class PostSearchRequest(BaseModel):
    keyword: str

class TagResponse(BaseModel):
    tag_name: str

class PostResponse(BaseModel):
    id: UUID4
    title: str
    description: str
    image_url: str
    tags: List[TagResponse] 
    average_rating: dict

    class Config:
        orm_mode = True
