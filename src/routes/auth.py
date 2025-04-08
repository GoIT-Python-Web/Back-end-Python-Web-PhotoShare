from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.security import create_access_token, create_refresh_token, verify_password
from src.repositories.user_repository import get_user_by_email, create_user
from src.schemas.user_schema import UserCreate, UserLogin, TokenModel
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
from fastapi import APIRouter, Body, Depends, HTTPException, status, Security, Request, BackgroundTasks, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.database.db import get_db
from src.entity.models import User, UserTypeEnum
from datetime import datetime
from src.entity.models import RefreshToken
from src.services.auth_service import store_tokens




router = APIRouter()

#перевірка токена
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")
async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):    
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])        
        user_id: UUID = UUID(payload.get("sub"))                
        user = await get_user_by_id(db, user_id)    
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
async def login(user_data: UserLogin, db: AsyncSession = Depends(get_db)):
    
        db_user = await get_user_by_username(db, user_data.username)
        if not db_user or not verify_password(user_data.password, db_user.password):
            raise HTTPException(status_code=400, detail="Invalid credentials")
    
        access_token, expire = create_access_token({"sub": str(db_user.id)})
        refresh_token = create_refresh_token({"sub": str(db_user.id)})
        await store_tokens({ "refresh_token": refresh_token}, db_user, db)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_at": expire.isoformat()
        }

@router.post("/logout")
async def logout(refresh_token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(RefreshToken).where(RefreshToken.token == refresh_token))
    token_obj = result.scalars().first()

    if not token_obj:
        raise HTTPException(status_code=404, detail="Refresh token not found")

    if token_obj.is_revoked:
        raise HTTPException(status_code=400, detail="Token already revoked")

    token_obj.revoked_at = datetime.utcnow()
    await db.commit()

    return {"message": "Token revoked successfully"}


@router.post("/refresh")
async def refresh_token(refresh_token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(RefreshToken).where(RefreshToken.token == refresh_token))
    token_obj = result.scalars().first()

    if not token_obj or token_obj.is_revoked:
        raise HTTPException(status_code=401, detail="Invalid or revoked refresh token")

    # можеш ще перевірити, чи не протух:
    if token_obj.expires_at < datetime.utcnow():
        raise HTTPException(status_code=401, detail="Refresh token expired")

    # Згенеруй нові токени
    access_token, expire = create_access_token({"sub": str(token_obj.user_id)})
    new_refresh_token = create_refresh_token({"sub": str(token_obj.user_id)})

    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "expires_at": expire.isoformat()
    }

