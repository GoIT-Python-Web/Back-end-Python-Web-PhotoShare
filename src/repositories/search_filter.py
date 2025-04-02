from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from sqlalchemy import func, asc, desc
from entity import Post, PostTag, PostRating
from schemas import PostSearchRequest, PostResponse, TagResponse
from typing import List

from repositories.rating_repository import get_rating_data

async def search_posts(query: PostSearchRequest, db: AsyncSession, sort_by: str, order: str) -> List[PostResponse]:
    stmt = (
        select(Post)
        .outerjoin(PostTag)
        .outerjoin(PostRating)
        .options(joinedload(Post.tags), joinedload(Post.ratings))
    )
    
    # Apply keyword search if provided
    if query.keyword:
        stmt = stmt.filter(
            (Post.title.ilike(f"%{query.keyword}%")) |
            (Post.description.ilike(f"%{query.keyword}%")) |
            (PostTag.tag_name.ilike(f"%{query.keyword}%"))
        )
    
    # Apply tag filtering if provided
    if query.tags:
        stmt = stmt.filter(PostTag.tag_name.ilike(f"%{query.tags}%"))
    
    # Apply sorting based on `sort_by` and `order`
    if sort_by == "rating":
        sort_column = func.avg(PostRating.stars)
    elif sort_by == "date":
        sort_column = Post.created_at
    else:
        sort_column = Post.created_at

    if order == "asc":
        stmt = stmt.order_by(asc(sort_column))
    else:
        stmt = stmt.order_by(desc(sort_column))

    result = await db.execute(stmt)
    posts = result.scalars().all()

    return [
        PostResponse(
            id=str(post.id),
            title=post.title,
            description=post.description,
            image_url=post.image_url,
            tags=[TagResponse(tag_name=tag.tag_name) for tag in post.tags],
            average_rating=await get_rating_data(post.id, db)
        )
        for post in posts
    ]
