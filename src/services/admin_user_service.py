from fastapi import HTTPException
from uuid import UUID
from src.entity.models import UserTypeEnum
from src.repositories.admin_user_repository import AdminUserRepository
from src.schemas.user_schema_for_admin_page import UserResponseForAdminPage

class AdminUserService:
    def __init__(self, db):
        self.repo = AdminUserRepository(db)

    async def admin_get_all_users(self):
        users = await self.repo.admin_get_all_users()
        return [UserResponseForAdminPage.model_validate(u) for u in users]

    async def admin_ban_user(self, user_id: UUID, admin):
        user = await self.repo.admin_get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if user.type == UserTypeEnum.admin:
            raise HTTPException(status_code=403, detail="Cannot ban another admin")

        user.is_active = not user.is_active
        await self.repo.admin_commit_and_refresh(user)

        action = "unbanned" if user.is_active else "banned"
        return {"message": f"User {user.email} has been {action} successfully"}


    async def admin_toggle_user_role(self, user_id: UUID):
        user = await self.repo.admin_get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        user.type = (
            UserTypeEnum.admin
            if user.type == UserTypeEnum.user
            else UserTypeEnum.user
        )
        await self.repo.admin_commit_and_refresh(user)

        return {
            "id": user.id,
            "new_role": user.type,
        }
