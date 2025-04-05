from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql.expression import Delete, Update
from src.entity.models import Post, User
from typing import Optional
from uuid import UUID
import datetime
from sqlalchemy.ext.asyncio import AsyncSession

class PostRepository:
    def __init__(self, user, db: AsyncSession):
        self.db = db
        self.user = user

    async def create(
            self, 
            title: str, 
            image_url: str, 
            description: Optional[str]
        ) -> Post:
        current_user = User()
        post = Post(
            user_id=current_user.id, 
            title=title, 
            image_url=image_url,
            description=description, 
            created_at = datetime.datetime.now(),
            updated_at = datetime.datetime.now()
        )
        self.db.add(post)
        await self.db.commit()
        await self.db.refresh(post)
        return post

    async def get_post(self, post_id: UUID) -> Post:
        stmt = select(Post).where(Post.id == post_id)
        result = await self.db.execute(stmt)

        return result.scalar_one_or_none()
    
    async def get_posts(self) -> list[Post]:
        stmt = select(Post)
        result = await self.db.execute(stmt)

        return result.scalars().all()
    
    async def update_post(self, post_id: UUID, description: Optional[str]) -> bool:
        stmt = Update(Post).where(Post.id == post_id).values(description=description)
        result = await self.db.execute(stmt)
        await self.db.commit()

        return result.rowcount > 0
    
    async def delete_post(self, post_id: UUID) -> bool:
        stmt = Delete(Post).where(Post.id == post_id)
        result = await self.db.execute(stmt)
        await self.db.commit()

        return result.rowcount > 0
