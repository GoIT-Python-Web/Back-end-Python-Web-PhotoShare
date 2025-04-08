from sqlalchemy.future import select
from src.entity.models import User

class AdminUserRepository:
    def __init__(self, db):
        self.db = db

    async def admin_get_all_users(self):
        result = await self.db.execute(select(User))
        return result.scalars().all()

    async def admin_get_user_by_id(self, user_id):
        return await self.db.get(User, user_id)

    async def admin_commit_and_refresh(self, instance):
        await self.db.commit()
        await self.db.refresh(instance)
