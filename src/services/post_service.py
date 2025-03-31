from src.repositories.post_repository import PostRepository
from uuid import UUID

class PostService:
    def __init__(self, post_repo: PostRepository):
        self.post_repo = post_repo

    async def get_post_by_id(self, post_id: UUID):
        return await self.post_repo.get_post(post_id)
    