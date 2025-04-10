from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from src.database.db import get_db
from src.core.dependencies import role_required
from src.schemas.user_schema_for_admin_page import UserResponseForAdminPage
from src.schemas.comment import CommentOut
from src.services.admin_user_service import AdminUserService
from src.services.admin_comment_service import AdminCommentService

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users", response_model=List[UserResponseForAdminPage])
async def admin_get_all_users(
    db: AsyncSession = Depends(get_db), admin=role_required("user", "admin")
):
    return await AdminUserService(db).admin_get_all_users()


@router.put("/users/{user_id}/ban", response_model=dict)
async def admin_ban_user(
    user_id: UUID, db: AsyncSession = Depends(get_db), admin=role_required("user", "admin")
):
    return await AdminUserService(db).admin_ban_user(user_id, admin)


@router.put("/toggle-role/{user_id}")
async def admin_toggle_user_role(
    user_id: UUID, db: AsyncSession = Depends(get_db), admin=role_required("user", "admin")
):
    return await AdminUserService(db).admin_toggle_user_role(user_id)


@router.delete("/comments/{comment_id}", response_model=dict)
async def admin_delete_comment(
    comment_id: UUID, db: AsyncSession = Depends(get_db), admin=role_required("user", "admin")
):
    return await AdminCommentService(db).admin_soft_delete_comment(comment_id)


@router.get("/posts/{post_id}/comments", response_model=List[CommentOut])
async def admin_get_post_comments(
    post_id: UUID, db: AsyncSession = Depends(get_db), admin=role_required("user", "admin")
):
    return await AdminCommentService(db).admin_get_post_comments(post_id)
