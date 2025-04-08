from uuid import UUID
from fastapi import HTTPException
from src.repositories.comment_repository import CommentRepository
from src.schemas.comment import CommentCreateDTO, CommentUpdateDTO
from src.entity.models import User

class CommentService:
    def __init__(self, comment_repo: CommentRepository):
        self.comment_repo = comment_repo

    async def add_comment(self, user_id: UUID, post_id: UUID, data: CommentCreateDTO):
        return await self.comment_repo.create(user_id, post_id, data.message)

    async def get_comments_for_post(self, post_id: UUID):
        return await self.comment_repo.get_by_post_id(post_id)

    async def get_comment(self, comment_id: UUID):
        comment = await self.comment_repo.get_by_id(comment_id)
        if comment is None:
            raise HTTPException(status_code=404, detail="Comment not found")
        return comment

    async def update_comment(self, comment_id: UUID, data: CommentUpdateDTO, current_user: User):
        comment = await self.comment_repo.get_by_id(comment_id)
        if comment is None or comment.user_id != current_user.id:
            raise HTTPException(status_code=404, detail="Comment not found or not authorized")
        return await self.comment_repo.update(comment_id, data.message)

    async def delete_comment(self, comment_id: UUID, current_user: User):
        comment = await self.comment_repo.get_by_id(comment_id)
        if comment is None or comment.user_id != current_user.id:
            raise HTTPException(status_code=404, detail="Comment not found or not authorized")
        return await self.comment_repo.delete(comment_id)



