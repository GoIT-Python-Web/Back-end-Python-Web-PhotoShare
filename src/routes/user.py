from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Request
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from src.database.db import get_db
from src.services.cloudinary_qr_service import UploadFileService
from src.repositories.edit_profile import update_user_profile
from src.repositories.admin_search_repository import get_user_by_id
from src.schemas.users import MyselfOut, UserProfileUpdate, UserProfileResponse
from src.entity.models import User
from src.core.security import get_current_user
from src.core.limiter import limiter


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=MyselfOut)
@limiter.limit("50/minute")
async def get_current_user_info(
    request: Request,
    current_user: User = Depends(get_current_user),
):
    return current_user


@router.get("/{user_id}", response_model=MyselfOut)
@limiter.limit("50/minute")
async def get_user(user_id: UUID, request: Request, db: AsyncSession = Depends(get_db)):
    user = await get_user_by_id(user_id, db)
    if not user:
        raise HTTPException(status_code=404, detail="Користувача не знайдено")
    return user


@router.put("/edit_profile", response_model=UserProfileResponse)
@limiter.limit("10/minute")
async def update_profile(request: Request,
    profile_data: UserProfileUpdate = Depends(),
    avatar: UploadFile = File(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    avatar_url = None
    if avatar and avatar.filename:
        avatar_url = await UploadFileService.upload_with_filters(avatar)

    return await update_user_profile(current_user.id, profile_data, db, avatar_url)
