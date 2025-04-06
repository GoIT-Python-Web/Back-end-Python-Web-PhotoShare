from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from repositories import users as users_repo
from schemas.user_schema import UserOut, UserSearchRequest
from entity.models import User
from core.dependencies import role_required

router = APIRouter(prefix="/admin/users", tags=["Admin Search"])

@router.get("/search", response_model=List[UserOut])
async def search_users(
    current_user: User = Depends(role_required("user", "admin")),
    filters: UserSearchRequest = Depends(),
    db: AsyncSession = Depends(get_db),
):
    return await users_repo.search_users(
        db=db,
        filters=filters,
        current_user_is_admin=current_user.type == "admin",
    )
