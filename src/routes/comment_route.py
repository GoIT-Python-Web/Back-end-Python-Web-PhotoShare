from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.db import get_db
from src.schemas.comment import CommentCreateDTO, CommentOut
from src.services.comment_service import CommentService
from src.repositories.comment_repository import CommentRepository
from uuid import UUID

router = APIRouter(prefix="/posts", tags=["comments"])

@router.post("/{post_id}/comments", response_model=CommentOut)
# async def add_comment(
#     post_id: UUID,
#     data: CommentCreateDTO,
#     db: AsyncSession = Depends(get_db),
#     user = Depends(get_current_user)
# ):
#     service = CommentService(CommentRepository(db))
#     return await service.add_comment(user.id, post_id, data)

@router.get("/{post_id}/comments", response_model=list[CommentOut])
async def get_comments(post_id: UUID, db: AsyncSession = Depends(get_db)):
    service = CommentService(CommentRepository(db))
    return await service.get_comments_for_post(post_id)
