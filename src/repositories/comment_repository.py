from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from src.entity.models import Comment
from uuid import UUID
from datetime import datetime

class CommentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, user_id: UUID, post_id: UUID, message: str) -> Comment:
        comment = Comment(user_id=user_id, post_id=post_id, message=message)
        self.db.add(comment)
        await self.db.commit()
        await self.db.refresh(comment)
        return comment

    async def update(self, comment_id: UUID, message: str) -> Comment | None:
        comment = await self.get_by_id(comment_id)
        if comment is None:
            return None
        comment.message = message
        comment.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(comment)
        return comment

    async def delete(self, comment_id: UUID) -> bool:
        comment = await self.get_by_id(comment_id)
        if comment is None:
            return False
        comment.is_deleted = True
        await self.db.commit()
        return True

    async def get_by_post_id(self, post_id: UUID) -> list[Comment]:
        result = await self.db.execute(
            select(Comment)
            .options(selectinload(Comment.user))
            .where(Comment.post_id == post_id)
            .order_by(Comment.created_at.asc())
        )
        return result.scalars().all()

    async def get_by_id(self, comment_id: UUID) -> Comment | None:
        result = await self.db.execute(
            select(Comment)
            .options(selectinload(Comment.user))
            .where(Comment.id == comment_id)
        )
        return result.scalar_one_or_none()
