from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.db import get_db
from src.schemas.comment import CommentCreateDTO, CommentOut, CommentUpdateDTO 
from src.services.comment_service import CommentService
from src.repositories.comment_repository import CommentRepository
from uuid import UUID
from fastapi import HTTPException
from src.entity.models import User
from src.core.dependencies import role_required

router = APIRouter(prefix="/posts", tags=["comments"])


@router.post("/{post_id}/comments", response_model=CommentOut)
async def add_comment(
    post_id: UUID,
    data: CommentCreateDTO,
    current_user: User = role_required("user", "admin"),
    db: AsyncSession = Depends(get_db)   
):
    service = CommentService(CommentRepository(db))
    return await service.add_comment(current_user.id, post_id, data)


@router.get("/{post_id}/comments", response_model=list[CommentOut])
async def get_comments(post_id: UUID, db: AsyncSession = Depends(get_db)):
    service = CommentService(CommentRepository(db))
    return await service.get_comments_for_post(post_id)


@router.get("/comments/{comment_id}", response_model=CommentOut)
async def get_comment(comment_id: UUID, db: AsyncSession = Depends(get_db)):
    service = CommentService(CommentRepository(db))
    return await service.get_comment(comment_id)


@router.put("/comments/{comment_id}", response_model=CommentOut)
async def update_comment(
    comment_id: UUID,
    data: CommentUpdateDTO,
    current_user: User = role_required("user", "admin"),
    db: AsyncSession = Depends(get_db),
):
    service = CommentService(CommentRepository(db))
    return await service.update_comment(comment_id, data, current_user)


@router.delete("/comments/{comment_id}")
async def delete_comment(
    comment_id: UUID,
    current_user: User = role_required("user", "admin"),
    db: AsyncSession = Depends(get_db),
):
    service = CommentService(CommentRepository(db))
    return {"success": await service.delete_comment(comment_id, current_user)}
