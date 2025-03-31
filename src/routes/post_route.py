from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas.post import PostResponse
from uuid import UUID
from src.database.db import get_db
from src.repositories.post_repository import PostRepository
from src.services.post_service import PostService

router = APIRouter(prefix='/post', tags=['posts'])

@router.get("/{post_id}", response_model=PostResponse)
async def get_post(post_id: UUID, db: AsyncSession = Depends(get_db)):
    service = PostService(PostRepository(db))
    
    return await service.get_post_by_id(post_id)