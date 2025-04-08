from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from sqlalchemy import func, asc, desc
from src.entity.models import Post, PostTag, PostRating
from src.schemas.search_filter import PostSearchRequest, PostResponse, TagResponse
from typing import List
from sqlalchemy import select, asc, desc, func, or_, and_, cast, Date
from src.repositories.rating_repository import get_rating_data

async def search_posts(
    filters: PostSearchRequest,
    db: AsyncSession
) -> List[PostResponse]:
    stmt = (
        select(Post)
        .outerjoin(PostTag)
        .outerjoin(PostRating)
        .options(joinedload(Post.tags), joinedload(Post.ratings), joinedload(Post.user))
    )

    filter_clauses = []

    if filters.keyword:
        filter_clauses.append(
            or_(
                Post.title.ilike(f"%{filters.keyword}%"),
                Post.description.ilike(f"%{filters.keyword}%"),
                PostTag.tag_name.ilike(f"%{filters.keyword}%")
            )
        )

    if filters.tags:
        filter_clauses.append(PostTag.tag_name.ilike(f"%{filters.tags}%"))

    if filters.from_date and filters.to_date:
        filter_clauses.append(Post.created_at.between(filters.from_date, filters.to_date))
    elif filters.from_date:
        filter_clauses.append(cast(Post.created_at, Date) == filters.from_date.date())
    elif filters.to_date:
        filter_clauses.append(cast(Post.created_at, Date) == filters.to_date.date())

    if filter_clauses:
        stmt = stmt.where(and_(*filter_clauses))

    if filters.sort_by == "rating":
        sort_column = func.avg(PostRating.rating)
    else:
        sort_column = Post.created_at

    if filters.order == "asc":
        stmt = stmt.order_by(asc(sort_column))
    else:
        stmt = stmt.order_by(desc(sort_column))

    result = await db.execute(stmt)
    posts = result.scalars().all()

    return [
        PostResponse(
            id=post.id,
            title=post.title,
            description=post.description,
            image_url=post.image_url,
            user_name=post.user.name,
            created_at=post.created_at,
            tags=[TagResponse(tag_name=tag.tag_name) for tag in post.tags],
            average_rating=await get_rating_data(post.id, db)
        )
        for post in posts
    ]