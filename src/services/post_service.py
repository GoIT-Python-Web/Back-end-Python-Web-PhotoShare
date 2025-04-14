from uuid import UUID
from typing import List, Optional
from src.repositories.post_repository import PostRepository
from src.schemas.post import PostResponse
from src.entity.models import Post

class PostService:
    def __init__(self, post_repo: PostRepository):
        self.post_repo = post_repo
        self.db = post_repo.db
    
    async def create_post(
        self,
        post_data: dict
    ):
        return await self.post_repo.create(post_data)

    async def get_post_by_id(self, post_id: UUID) -> PostResponse:
        return await self.post_repo.get_post(post_id)

    async def get_all_posts(self) -> List[PostResponse]:
        return await self.post_repo.get_posts()
    
    async def get_all_user_posts(self) -> List[PostResponse]:
        return await self.post_repo.get_user_posts()

    async def update_post(
        self,
        post_id: UUID,
        description: Optional[str] = None
    ) -> PostResponse:
        return await self.post_repo.update_post(post_id, description)

    async def delete_post(self, post_id: UUID) -> bool:
        return await self.post_repo.delete_post(post_id)
    
    async def is_author_or_admin(self, post: Post):
        return await self.post_repo.is_author_or_admin(post)
    