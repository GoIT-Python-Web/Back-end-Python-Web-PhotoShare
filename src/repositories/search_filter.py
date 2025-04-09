from datetime import timedelta
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
        words = [word.strip() for word in filters.keyword.split(',') if word.strip()]
        keyword_conditions = []
        
        for word in words:
            keyword_conditions.append(
                or_(
                    Post.title.ilike(f"%{word}%"),
                    Post.description.ilike(f"%{word}%"),
                    PostTag.tag_name.ilike(f"%{word}%")
                )
            )

        filter_clauses.append(or_(*keyword_conditions))

    if filters.tags:
        filter_clauses.append(PostTag.tag_name.ilike(f"%{filters.tags}%"))

    if filters.from_date and filters.to_date:
        to_date = filters.to_date + timedelta(days=1)
        filter_clauses.append(Post.created_at.between(filters.from_date, to_date))
    elif filters.from_date:
        filter_clauses.append(cast(Post.created_at, Date) == filters.from_date.date())
    elif filters.to_date:
        filter_clauses.append(cast(Post.created_at, Date) == filters.to_date.date())

    if filter_clauses:
        stmt = stmt.where(and_(*filter_clauses))

    stmt = stmt.group_by(Post.id)

    if filters.rating_to is not None:
        stmt = stmt.having(func.avg(PostRating.rating) <= filters.rating_to)

    if filters.sort_by == "rating":
        stmt = stmt.group_by(Post.id)
        sort_column = func.avg(PostRating.rating)
    else:
        sort_column = Post.created_at

    if filters.order == "asc":
        stmt = stmt.order_by(asc(sort_column))
    else:
        stmt = stmt.order_by(desc(sort_column))

    result = await db.execute(stmt)
    posts = result.unique().scalars().all()
    
    return [
        PostResponse(
            id=post.id,
            title=post.title,
            description=post.description,
            image_url=post.image_url,
            user_name=post.user.name,
            created_at=post.created_at,
            tags=[TagResponse(tag_name=tag.tag_name) for tag in post.tags],
            avg_rating=average_rating,
            rating_count=total_reviews
        )
        for post in posts
        for average_rating, total_reviews in [await get_rating_data(post.id, db)]
    ]