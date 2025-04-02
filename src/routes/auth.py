from fastapi import APIRouter, Body, Depends, HTTPException, status, Security, Request, BackgroundTasks, Form


from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from datetime import datetime # лише для фейкового адміна
from uuid import UUID # лише для фейкового адміна

from src.database.db import get_db
from src.entity.models import User, UserTypeEnum


async def get_current_user(email: str, db: AsyncSession = Depends(get_db)) -> User | None:
    query = select(User).filter_by(email=email)
    user = await db.execute(query)
    return user.scalar_one_or_none()


async def get_current_admin(db: AsyncSession = Depends(get_db)) -> User:
    """Отримання адміністратора з бази даних (або створення, якщо не існує)"""

    query = select(User).filter_by(email="admin@example.com")
    result = await db.execute(query)
    admin = result.scalars().first()

    if not admin:
        # Якщо адміністратор не знайдений:
        admin = User(
            id=UUID("00000000-0000-0000-0000-000000000000"),
            username="admin",
            name="Admin User",
            email="admin@example.com",
            phone="1234567890",
            type=UserTypeEnum.admin,
            birthdate=None,
            password="fake_hashed_password",
            description="This is a temporary admin user.",
            img_link=None,
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(admin)
        await db.commit()
        await db.refresh(admin)

    if admin.type != UserTypeEnum.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    return admin
