from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.db import get_db
from src.services.cloudinary_qr_service import UploadFileService
from src.repositories.edit_profile import update_user_profile
from src.schemas.users import MyselfOut, UserProfileUpdate, UserProfileResponse
from src.entity.models import User
from src.core.security import get_current_user


router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=MyselfOut)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
):
    return current_user


@router.put("/edit_profile", response_model=UserProfileResponse)
async def update_profile(
    profile_data: UserProfileUpdate = Depends(),
    avatar: UploadFile = File(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    avatar_url = None
    if avatar and avatar.filename:
        avatar_url = await UploadFileService.upload_file(avatar)

    return await update_user_profile(current_user.id, profile_data, db, avatar_url)