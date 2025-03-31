from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.entity.models import Post
from uuid import UUID

class PostRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_post(self, post_id: UUID) -> Post:
        stmt = select(Post).where(Post.id == post_id)
        result = await self.db.execute(stmt)

        return result.scalar_one_or_none()
