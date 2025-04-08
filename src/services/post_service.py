from uuid import UUID
from typing import List, Optional

from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from src.repositories.post_repository import PostRepository
from src.schemas.post import PostResponse
from src.entity.models import Post, PostRating, PostTag


class PostService:
    def __init__(self, post_repo: PostRepository):
        self.post_repo = post_repo
        self.db = post_repo.db  # предполагается, что у PostRepository есть self.db
    async def create_post(
        self,
        title: str,
        image_url: str,
        description: Optional[str] = None
    ):
        return await self.post_repo.create(title, image_url, description)

    async def get_post_by_id(self, post_id: UUID) -> PostResponse:
        return await self.post_repo.get_post(post_id)

    async def get_all_posts(self) -> List[PostResponse]:
        return await self.post_repo.get_posts()

    async def update_post(
        self,
        post_id: UUID,
        description: Optional[str] = None
    ) -> PostResponse:
        return await self.post_repo.update_post(post_id, description)

    async def delete_post(self, post_id: UUID) -> bool:
        return await self.post_repo.delete_post(post_id)