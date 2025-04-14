from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.db import get_db
from src.repositories.search_filter import search_posts
from src.schemas.search_filter import PostSearchRequest, PostResponse
from typing import List, Optional
from src.core.limiter import limiter


router = APIRouter(prefix="/posts", tags=["Post Search"])


@router.get("/search", response_model=List[PostResponse])
@limiter.limit("10/minute")
async def search_posts_with_filters(
    request: Request,
    filters: PostSearchRequest = Depends(),
    db: AsyncSession = Depends(get_db),
):
    return await search_posts(filters, db)
