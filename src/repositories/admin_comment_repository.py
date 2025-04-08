from sqlalchemy.future import select
from src.entity.models import Comment

class AdminCommentRepository:
    def __init__(self, db):
        self.db = db

    async def admin_get_comment_by_id(self, comment_id):
        return await self.db.get(Comment, comment_id)

    async def admin_commit(self):
        await self.db.commit()

    async def admin_get_post_comments(self, post_id):
        result = await self.db.execute(
            select(Comment).where(Comment.post_id == post_id, Comment.is_deleted == False)
        )
        return result.scalars().all()
