from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql import func, select
from pydantic import BaseModel, Field
from src.database.db import get_db
from src.entity.models import User, Post, PostRating
from src.repositories.rating_repository import add_rating, get_rating_data
from src.routes.auth import get_current_user


router = APIRouter(prefix="/ratings", tags=["ratings"])


class RatingRequest(BaseModel):
    rating: int = Field(ge=1, le=5)

@router.post("/posts/{post_id}/rate")
async def rate_post(post_id: int, rating_data: RatingRequest, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await add_rating(post_id, rating_data.rating, db, current_user)

@router.get("/posts/{post_id}/rating")
async def get_post_rating(post_id: int, db: AsyncSession = Depends(get_db)):
    return await get_rating_data(post_id, db)