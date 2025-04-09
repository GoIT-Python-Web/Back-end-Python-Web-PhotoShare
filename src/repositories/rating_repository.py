from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql import func
from fastapi import HTTPException
from src.entity.models import Post, PostRating, User

async def add_rating(post_id: UUID, rating: int, db: AsyncSession, current_user: User) -> PostRating:
    # Check if the post exists
    result = await db.execute(select(Post).filter(Post.id == post_id))
    post = result.scalars().first()
    if not post:
        raise HTTPException(status_code=404, detail="Пост не знайдено")
    
    # Prevent user from rating their own post
    if post.user_id == current_user.id:
        raise HTTPException(status_code=403, detail="Ви не можете оцінювати власні пости")
    
    # Check if the user already rated this post
    result = await db.execute(select(PostRating).filter(PostRating.post_id == post_id, PostRating.user_id == current_user.id))
    existing_rating = result.scalars().first()
    if existing_rating:
        raise HTTPException(status_code=400, detail="Ви вже оцінили даний пост")
    
    # Add new rating
    new_rating = PostRating(post_id=post_id, user_id=current_user.id, rating=rating)
    db.add(new_rating)
    await db.commit()
    await db.refresh(new_rating)
    return new_rating

async def get_rating_data(post_id: UUID, db: AsyncSession):
    # Check if the post exists
    result = await db.execute(select(Post).filter(Post.id == post_id))
    post = result.scalars().first()
    if not post:
        raise HTTPException(status_code=404, detail="Пост не знайдено")
    
    # Get average rating and total number of ratings
    result = await db.execute(select(func.avg(PostRating.rating), func.count(PostRating.id)).filter(PostRating.post_id == post_id))
    rating_data = result.first()
    average_rating = round(rating_data[0], 1) if rating_data[0] else 0
    total_reviews = rating_data[1]
    return {"rating":f"{average_rating} / 5 ({total_reviews} оцінок)"}