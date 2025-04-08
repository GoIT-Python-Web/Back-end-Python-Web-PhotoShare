from fastapi import HTTPException
from uuid import UUID
from src.repositories.admin_comment_repository import AdminCommentRepository

class AdminCommentService:
    def __init__(self, db):
        self.repo = AdminCommentRepository(db)

    async def admin_soft_delete_comment(self, comment_id: UUID):
        comment = await self.repo.admin_get_comment_by_id(comment_id)
        if not comment:
            raise HTTPException(status_code=404, detail="Comment not found")

        comment.is_deleted = True
        await self.repo.admin_commit()
        return {"message": "Comment marked as deleted"}

    async def admin_get_post_comments(self, post_id: UUID):
        return await self.repo.admin_get_post_comments(post_id)
