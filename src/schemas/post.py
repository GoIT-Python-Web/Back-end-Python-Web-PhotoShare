from datetime import date
from pydantic import BaseModel
from pydantic.config import ConfigDict

class PostModel(BaseModel):
    title: str
    description: str
    created_at: date = None

    model_config = ConfigDict(from_attributes=True)

class PostResponse(BaseModel):
    title: str
    description: str
    created_at: date = None

    model_config = ConfigDict(from_attributes=True)