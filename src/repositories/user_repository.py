from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.entity.models import User
from src.schemas.user_schema import UserCreate
from src.core.security import get_password_hash


async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(select(User).filter(User.email == email))
    return result.scalars().first()

async def create_user(db: AsyncSession, user_data: UserCreate):
    password = get_password_hash(user_data.password)
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        type=user_data.type,
        password=password,
        
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

