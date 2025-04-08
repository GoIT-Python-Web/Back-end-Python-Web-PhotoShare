from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.sql import func
from sqlalchemy.sql.expression import Delete, Update
from src.entity.models import Post, PostRating, PostTag, User
from src.schemas.post import PostResponse, TagsShortResponse
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
        post = Post(
            user_id=self.user.id, 
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
        stmt = (
            select(Post)
            .options(
                joinedload(Post.user),
                selectinload(Post.tags).selectinload(PostTag.tag),
                selectinload(Post.ratings)
            )
            .where(Post.id == post_id)
        )

        result = await self.db.execute(stmt)

        post = result.scalar_one_or_none()

        if not post:
            return None
        
        post_response = PostResponse.from_orm(post)
        post_response.avg_rating = (
            round(sum(r.rating for r in post.ratings) / len(post.ratings), 2)
            if post.ratings else None
        )
        post_response.rating_count = len(post.ratings)
        post_response.tags = [
            TagsShortResponse.from_orm(tag_rel.tag)
            for tag_rel in post.tags
            if tag_rel.tag is not None
        ]

        return post_response
    
    async def get_posts(self) -> list[Post]:
        stmt = (select(
            Post
        ).options(
            joinedload(Post.user),
            selectinload(Post.tags).selectinload(PostTag.tag),
            selectinload(Post.ratings)
        )
        )

        result = await self.db.execute(stmt)

        posts = result.scalars().all()
    
        posts_response = []

        for post in posts:
            avg = round(sum(r.rating for r in post.ratings) / len(post.ratings), 2) if post.ratings else None
            count = len(post.ratings)

            post_response = PostResponse.from_orm(post)
            post_response.avg_rating = avg
            post_response.rating_count = count

            post_response.tags = [
            TagsShortResponse.from_orm(tag_rel.tag)
                for tag_rel in post.tags
                if tag_rel.tag is not None
            ]

            posts_response.append(post_response)

        return posts_response
    
    async def update_post(self, post_id: UUID, description: Optional[str]) -> Post:
        stmt = Update(Post).where(Post.id == post_id).values(description=description)
        await self.db.execute(stmt)
        await self.db.commit()

        post = await self.get_post(post_id)

        return post
    
    async def delete_post(self, post_id: UUID) -> bool:
        stmt = Delete(Post).where(Post.id == post_id)
        result = await self.db.execute(stmt)
        await self.db.commit()

        return result.rowcount > 0
    
    