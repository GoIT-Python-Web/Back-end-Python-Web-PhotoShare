from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.db import get_db
from src.repositories import admin_search_repository as users_repo
from src.schemas.admin_search import UserOut, UserSearchRequest
from src.entity.models import User
from src.core.dependencies import role_required

router = APIRouter(prefix="/admin/users", tags=["Admin Search"])

@router.get("/search", response_model=List[UserOut])
async def search_users(
    current_user: User = role_required("admin"),
    filters: UserSearchRequest = Depends(),
    db: AsyncSession = Depends(get_db),
):
    return await users_repo.search_users(
        db=db,
        filters=filters,
        current_user_is_admin=current_user.type == "admin",
    )
