from sqlalchemy.orm import Session
from src.entity.models import User
from src.schemas.user_schema import UserCreate
from src.core.security import get_password_hash
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select


async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(select(User).filter(User.email == email))
    return result.scalars().first()

async def create_user(db: AsyncSession, user_data):
    new_user = User(**user_data)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user
