from fastapi import APIRouter, Body, Depends, HTTPException, status, Security, Request, BackgroundTasks, Form


from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from datetime import datetime # лише для фейкового адміна
from uuid import UUID # лише для фейкового адміна

from src.database.db import get_db
from src.entity.models import User, UserTypeEnum
from src.schemas.user_schema import TokenModel


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
            password="fake_password",
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



from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.security import create_access_token, create_refresh_token, verify_password
from src.repositories.user_repository import get_user_by_email, create_user
from src.schemas.user_schema import UserCreate, UserLogin
from src.database.db import get_db
from src.entity.models import User
from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import date

router = APIRouter()

@router.post("/register")
async def register(
    username: str,
    email: EmailStr,
    password: str,
    
    name: Optional[str] = None,
    phone: Optional[str] = None,
    birthdate: Optional[date] = None,
    description: Optional[str] = None,
    img_link: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    existing_user = await get_user_by_email(db, email)

    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    is_admin = (await db.execute(select(User))).scalars().first()  # Перший юзер = admin
    if is_admin:
        type = UserTypeEnum.admin
    else:
        type = UserTypeEnum.user

    user = UserCreate(
        username=username,
        email=email,
        password=password,  # Пароль замінимо після хешування
        type=type,
        name=name,
        phone=phone,
        birthdate=birthdate,
        description=description,
        img_link=img_link
    )
    return await create_user(db, user) 

@router.post("/login", response_model=TokenModel)
async def login(email : str, password : str, db: AsyncSession = Depends(get_db)):
    db_user = await get_user_by_email(db, email)
    if not db_user or not verify_password(password, db_user.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    return {
        "access_token": create_access_token({"sub": db_user.email }),
        "refresh_token": create_refresh_token({"sub": db_user.email}),
    }
