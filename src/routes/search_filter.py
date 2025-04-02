from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_async_db
from repositories.search_filter import search_posts
from schemas import PostSearchRequest, PostResponse
from typing import List, Optional

router = APIRouter()

@router.get("/posts/search", response_model=List[PostResponse])
async def search_posts_with_filters(
    keyword: Optional[str] = None,
    tags: Optional[str] = None,
    sort_by: Optional[str] = "date",  # Default to sorting by date
    order: Optional[str] = "desc",    # Default to descending order
    db: AsyncSession = Depends(get_async_db)
):
    query = PostSearchRequest(keyword=keyword, tags=tags)
    return await search_posts(query, db, sort_by, order)
