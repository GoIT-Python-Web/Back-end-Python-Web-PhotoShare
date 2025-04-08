from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
from src.conf.config import settings
from sqlalchemy.ext.asyncio import AsyncSession
from src.entity.models import User, RefreshToken
from uuid import uuid4

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, password: str) -> bool:
    return pwd_context.verify(plain_password, password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")

def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=7)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")

async def store_tokens(data: dict, user: User, db: AsyncSession):

    db_token = RefreshToken(
        id=uuid4(),
        user_id=user.id,
        token=data["refresh_token"],
        
        created_at=datetime.utcnow(),
        expires_at=datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )
    db.add(db_token)
    await db.commit()
    await db.refresh(db_token)

    return "token is saved"
    
