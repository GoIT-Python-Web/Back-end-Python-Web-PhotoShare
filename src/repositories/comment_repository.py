from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.entity.models import Comment
from uuid import UUID

class CommentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, user_id: UUID, post_id: UUID, message: str) -> Comment:
        comment = Comment(user_id=user_id, post_id=post_id, message=message)
        self.db.add(comment)
        await self.db.commit()
        await self.db.refresh(comment)
        return comment

    async def get_by_post_id(self, post_id: UUID) -> list[Comment]:
        result = await self.db.execute(
            select(Comment).where(Comment.post_id == post_id).order_by(Comment.created_at.asc())
        )
        return result.scalars().all()

