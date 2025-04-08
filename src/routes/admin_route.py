from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from uuid import UUID
import logging # для дебагу лише

from src.database.db import get_db
from src.entity.models import User, UserTypeEnum, Post, Comment, PostRating

from src.core.security import get_current_user
from src.core.dependencies import role_required

from src.schemas.user_schema_for_admin_page import UserResponseForAdminPage
from src.schemas.comment import CommentOut
from src.schemas.rating import RatingOut

router = APIRouter(prefix="/admin", tags=["admin"])


logging.basicConfig(level=logging.INFO) # для дебагу лише
logger = logging.getLogger(__name__) # для дебагу лише


# ============ 1. Отримання всіх користувачів - GET /admin/users ============
@router.get("/users", response_model=List[UserResponseForAdminPage])
async def get_all_users(db: AsyncSession = Depends(get_db), admin: User = role_required("user", "admin")):
    """
    Отримання списку всіх користувачів (лише для адміністратора).
    """
    result = await db.execute(select(User))
    users = result.scalars().all()
    return [UserResponseForAdminPage.model_validate(user) for user in users]


# ============ 2. Блокування користувача - PUT /admin/users/{user_id}/ban ============
@router.put("/users/{user_id}/ban", response_model=dict)
async def ban_user(
    user_id: UUID, 
    db: AsyncSession = Depends(get_db), 
    admin: User = role_required("user", "admin")  # Перевірка ролі
):
    """Блокування користувача (адміністратором)."""
    logger.info(f"Admin {admin.email} is trying to ban user {user_id}")

    user = await db.get(User, user_id)
    if not user:
        logger.error(f"User {user_id} not found")
        raise HTTPException(status_code=404, detail="User not found")

    if user.type == UserTypeEnum.admin:
        logger.warning(f"Attempt to ban another admin: {user.email}")
        raise HTTPException(status_code=403, detail="Cannot ban another admin")

    if not user.is_active:
        logger.info(f"User {user.email} is already banned")
        raise HTTPException(status_code=400, detail="User is already banned")

    user.is_active = False
    await db.commit()
    await db.refresh(user)

    logger.info(f"User {user.email} has been banned successfully")
    return {"message": f"User {user.email} has been banned successfully"}


# ============ 3. Видалення коментарів (soft delete) - DELETE /admin/comments/{comment_id} ============
@router.delete("/comments/{comment_id}", response_model=dict)
async def delete_comment(comment_id: UUID, db: AsyncSession = Depends(get_db), admin: User = role_required("user", "admin")):
    """
    Видалення коментаря адміністратором (soft delete).
    """
    comment = await db.get(Comment, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    comment.is_deleted = True
    await db.commit()
    return {"message": "Comment marked as deleted"}


# ============ 4. Отримання коментарів до поста (без видалених) - GET /admin/posts/{post_id}/comments ============
@router.get("/posts/{post_id}/comments", response_model=List[CommentOut])
async def get_post_comments(post_id: UUID, db: AsyncSession = Depends(get_db), admin: User = role_required("user", "admin")):
    """
    Отримання списку коментарів до поста (без врахування видалених).
    """
    result = await db.execute(select(Comment).where(Comment.post_id == post_id, Comment.is_deleted == False))
    return result.scalars().all()


# ============ 5. Зміна ролі користувача на протилежну - PUT /toggle-role/{user_id} ============
@router.put("/toggle-role/{user_id}")
async def toggle_user_role(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    admin: User = role_required("user", "admin")
):
    """
    Зміна ролі користувача на протилежну (user/admin)
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.type = UserTypeEnum.admin if user.type == UserTypeEnum.user else UserTypeEnum.user

    await db.commit()
    await db.refresh(user)

    return {
        "id": user.id,
        "new_role": user.type,
    }