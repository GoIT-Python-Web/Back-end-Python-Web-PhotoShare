from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.sql import func
from sqlalchemy.sql.expression import Delete, Update
from src.entity.models import Post, PostTag, Tag
from src.schemas.post import PostResponse, PostCreateResponse, TagsShortResponse
from typing import Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

import datetime

class PostRepository:
    def __init__(self, db: AsyncSession, user = None, user_id = None):
        self.db = db
        self.user = user
        self.user_id = user_id

    async def create(
            self, 
            post_data: dict
        ) -> Post:

        post = Post(
            user_id=self.user.id, 
            title=post_data.title, 
            description=post_data.description,
            image_url=post_data.image_url,
            location=post_data.location,
            created_at = datetime.datetime.now(),
            updated_at = datetime.datetime.now()
        )

        self.db.add(post)
        await self.db.flush()

        tag_names = post_data.tags

        for tag_model in tag_names:
            stmt = select(Tag).where(Tag.name == tag_model.name)
            result = await self.db.execute(stmt)
            tag = result.scalar_one_or_none()

            if not tag:
                tag = Tag(name=tag_model.name)
                self.db.add(tag)
                await self.db.flush()

            stmt = select(PostTag).where(
                PostTag.post_id == post.id, 
                PostTag.tag_name == tag_model.name
            )
            result = await self.db.execute(stmt)
            post_tag_exists = result.scalar_one_or_none()

            if not post_tag_exists:
                post_tag = PostTag(post_id=post.id, tag_name=tag_model.name)
                self.db.add(post_tag)
                
            await self.db.commit()
            await self.db.refresh(post)
        post_response = PostCreateResponse.model_validate(post)

        return post_response

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
            raise HTTPException(status_code=404, detail="Post not found")
        
        post_response = PostResponse.model_validate(post)
        
        post_response.avg_rating = (
            round(sum(r.rating for r in post.ratings) / len(post.ratings), 2)
            if post.ratings else None
        )
        post_response.rating_count = len(post.ratings)

        post_response.tags = []
        post_response.tags = [
            TagsShortResponse.model_validate(tag_rel.tag)
            for tag_rel in post.tags
            if tag_rel.tag is not None
        ]

        return post_response
    
    async def get_user_posts(self) -> list[Post]:
        user_id = self.user_id

        stmt = (select(
            Post
        ).options(
            joinedload(Post.user),
            selectinload(Post.tags).selectinload(PostTag.tag),
            selectinload(Post.ratings)
        ).where(Post.user_id == user_id)
        .order_by(Post.created_at.desc())
        )

        result = await self.db.execute(stmt)

        posts = result.scalars().all()
    
        posts_response = []

        for post in posts:
            avg = round(sum(r.rating for r in post.ratings) / len(post.ratings), 2) if post.ratings else None
            count = len(post.ratings)

            post_response = PostResponse.model_validate(post)
            post_response.avg_rating = avg
            post_response.rating_count = count

            post_response.tags = [
            TagsShortResponse.model_validate(tag_rel.tag)
                for tag_rel in post.tags
                if tag_rel.tag is not None
            ]

            posts_response.append(post_response)

        return posts_response
    
    async def get_posts(self) -> list[Post]:
        stmt = (select(
            Post
        ).join(Post.user)
        .where(Post.user.has(is_active=True))
        .options(
            joinedload(Post.user),
            selectinload(Post.tags).selectinload(PostTag.tag),
            selectinload(Post.ratings)
        ).order_by(Post.created_at.desc())
        )

        result = await self.db.execute(stmt)

        posts = result.scalars().all()
    
        posts_response = []

        for post in posts:
            avg = round(sum(r.rating for r in post.ratings) / len(post.ratings), 2) if post.ratings else None
            count = len(post.ratings)

            post_response = PostResponse.model_validate(post)
            post_response.avg_rating = avg
            post_response.rating_count = count

            post_response.tags = [
            TagsShortResponse.model_validate(tag_rel.tag)
                for tag_rel in post.tags
                if tag_rel.tag is not None
            ]

            posts_response.append(post_response)

        return posts_response
    
    async def update_post(self, post_id: UUID, description: Optional[str]) -> Post:
        stmt = Update(Post).where(Post.id == post_id).values(
            description=description,
            updated_at = datetime.datetime.now()
        )
        await self.db.execute(stmt)
        await self.db.commit()

        post = await self.get_post(post_id)

        return post
    
    async def delete_post(self, post_id: UUID) -> bool:
        stmt = Delete(Post).where(Post.id == post_id)
        result = await self.db.execute(stmt)
        await self.db.commit()

        return result.rowcount > 0
    
    async def is_author_or_admin(self, post: Post) -> bool:
        return self.user.id == post.user_id or self.user.type == "admin"
  