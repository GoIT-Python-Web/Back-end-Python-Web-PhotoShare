from fastapi import APIRouter, Body, Depends, HTTPException, status, Security, Request, BackgroundTasks, Form


from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.database.db import get_db
from src.entity.models import User


async def get_current_user(email: str, db: AsyncSession = Depends(get_db)) -> User | None:
    query = select(User).filter_by(email=email)
    user = await db.execute(query)
    return user.scalar_one_or_none()



from sqlalchemy.orm import Session
from src.core.security import create_access_token, create_refresh_token, verify_password, get_password_hash
from src.repositories.user_repository import get_user_by_email, create_user
from src.schemas.user_schema import UserCreate, UserLogin

router = APIRouter()

@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = get_user_by_email(db, user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    is_admin = db.query(User).count() == 0  # Перший юзер = admin
    return create_user(db, user, is_admin)

@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, user.email)
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    return {
        "access_token": create_access_token({"sub": db_user.email, "is_admin": db_user.is_admin}),
        "refresh_token": create_refresh_token({"sub": db_user.email}),
    }
