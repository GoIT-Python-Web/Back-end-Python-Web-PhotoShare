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


#---------------------------JWT-------------------------------------------------
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
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from src.conf.config import settings
from src.repositories.user_repository import get_user_by_email, get_user_by_id, create_user, get_user_by_username
from uuid import UUID
from src.database.db import get_db
from sqlalchemy.exc import SQLAlchemyError
router = APIRouter()

#перевірка токена
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")
async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        
        user_id: UUID = UUID(payload.get("sub"))

        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await get_user_by_id(db, user_id)
    if user is None:
        raise credentials_exception

    return user

@router.post("/register")
async def register(
    user: UserCreate = Body(...),  
    
    db: AsyncSession = Depends(get_db)):


    existing_user = await get_user_by_email(db, user.email)

    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    user_exists = (await db.execute(select(User))).scalars().first()  # Перший юзер = admin
    if not user_exists:
        user_type = UserTypeEnum.admin
    else:
        user_type = UserTypeEnum.user

    return await create_user(db, user, user_type) 

@router.post("/login", response_model=TokenModel)
async def login(username: str = Form(...), password: str = Form(...), db: AsyncSession = Depends(get_db)):
    
        db_user = await get_user_by_username(db, username)
        if not db_user or not verify_password(password, db_user.password):
            raise HTTPException(status_code=400, detail="Invalid credentials")
    
        access_token, expire = create_access_token({"sub": str(db_user.id)})
        refresh_token = create_refresh_token({"sub": str(db_user.id)})
        
        

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_at": expire.isoformat()
        }
