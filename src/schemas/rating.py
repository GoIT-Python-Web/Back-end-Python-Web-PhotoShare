from pydantic import BaseModel, UUID4, Field
from datetime import datetime



class RatingCreate(BaseModel):
    rating: int = Field(ge=1, le=5)


class RatingOut(BaseModel):
    id: UUID4
    user_id: UUID4
    post_id: UUID4
    rating: int = Field(ge=1, le=5)

    model_config = {
        "from_attributes": True 
    }