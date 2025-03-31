from uuid import UUID
from repositories.comment_repository import CommentRepository
from schemas.comment import CommentCreateDTO

class CommentService:
    def __init__(self, comment_repo: CommentRepository):
        self.comment_repo = comment_repo

    async def add_comment(self, user_id: UUID, post_id: UUID, data: CommentCreateDTO):
        return await self.comment_repo.create(user_id, post_id, data.message)

    async def get_comments_for_post(self, post_id: UUID):
        return await self.comment_repo.get_by_post_id(post_id)

