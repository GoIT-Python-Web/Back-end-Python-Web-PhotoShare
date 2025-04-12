from fastapi import HTTPException
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update, select
from src.entity.models import User
from src.schemas.users import UserProfileUpdate
from src.core.security import get_password_hash


async def update_user_profile(user_id: UUID, data: UserProfileUpdate, db: AsyncSession, avatar_url: str = None):
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    clean_data = {k: v for k, v in data.dict(exclude_unset=True).items() if v not in [None, ""]}

    if 'password' in clean_data:
        raw_password = clean_data.pop('password')
        clean_data['password'] = get_password_hash(raw_password)

    for field, value in clean_data.items():
        setattr(user, field, value)

    if avatar_url:
        user.img_link = avatar_url
    
    await db.commit()
    await db.refresh(user)
    return user
