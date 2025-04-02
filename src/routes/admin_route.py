from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from uuid import UUID
import logging # для дебагу лише

from src.database.db import get_db
from src.entity.models import User, Post, Comment
from src.routes.auth import get_current_admin
from src.schemas.fake_user_schema_by_pavlo import UserBase, UserTypeEnum
from src.schemas.comment import CommentOut

router = APIRouter(prefix="/admin", tags=["admin"])


logging.basicConfig(level=logging.INFO) # для дебагу лише
logger = logging.getLogger(__name__) # для дебагу лише


# ============ 1. Отримання всіх користувачів - GET /admin/users ============
@router.get("/users", response_model=List[UserBase])
async def get_all_users(db: AsyncSession = Depends(get_db), admin: User = Depends(get_current_admin)):
    """
    Отримання списку всіх користувачів (лише для адміністратора).
    Якщо користувач не є адміністратором, буде повернута помилка доступу.
    """
    if admin.type != UserTypeEnum.admin:
        raise HTTPException(status_code=403, detail="Access denied: Only admins can view all users")

    result = await db.execute(select(User))
    users = result.scalars().all()

    return [UserBase.model_validate(user) for user in users]



# ============ 2. Блокування користувача - PUT /admin/users/{user_id}/ban ============
@router.put("/users/{user_id}/ban", response_model=dict)
async def ban_user(
    user_id: UUID, 
    db: AsyncSession = Depends(get_db), 
    admin: User = Depends(get_current_admin)  # Авторизація
):
    """Блокування користувача (адміністратором)."""

    logger.info(f"Admin {admin.email} is trying to ban user {user_id}")

    user = await db.get(User, user_id)
    if not user:
        logger.error(f"User {user_id} not found")
        raise HTTPException(status_code=404, detail="User not found")

    logger.info(f"Found user: {user.email} | Active: {user.is_active}")

    if user.type == UserTypeEnum.admin:
        logger.warning(f"Attempt to ban another admin: {user.email}")
        raise HTTPException(status_code=403, detail="Cannot ban another admin")

    if not user.is_active:
        logger.info(f"User {user.email} is already banned")
        raise HTTPException(status_code=400, detail="User is already banned")

    user.is_active = False
    await db.commit()
    await db.refresh(user)  # Оновлюємо об'єкт у сесії

    logger.info(f"User {user.email} has been banned successfully")

    return {"message": f"User {user.email} has been banned successfully"}



# ============ 3. Видалення коментарів (soft delete) - DELETE /admin/comments/{comment_id} ============
@router.delete("/comments/{comment_id}", response_model=dict)
async def delete_comment(comment_id: UUID, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_admin)):
    """
    Видалення коментаря адміністратором (soft delete).
    """
    comment = await db.get(Comment, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    comment.is_deleted = True
    await db.commit()
    await db.refresh(user)
    return {"message": "Comment marked as deleted"}


# ============ 4. Отримання коментарів до поста (без видалених) - GET /admin/posts/{post_id}/comments ============
@router.get("/posts/{post_id}/comments", response_model=List[CommentOut])
async def get_post_comments(post_id: UUID, db: AsyncSession = Depends(get_db)):
    """
    Отримання списку коментарів до поста (без врахування видалених).
    """
    result = await db.execute(select(Comment).where(Comment.post_id == post_id, Comment.is_deleted == False))
    return result.scalars().all()
