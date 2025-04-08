from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
from src.conf.config import settings
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.entity.models import User, RefreshToken
from uuid import uuid4
import secrets

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, password: str) -> bool:
    return pwd_context.verify(plain_password, password)


def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=15)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    return encoded_jwt, expire


async def get_or_create_refresh_token(user: User, db: AsyncSession) -> str:
    stmt = select(RefreshToken).where(
        RefreshToken.user_id == user.id,
        RefreshToken.revoked_at.is_(None),
        RefreshToken.expires_at > datetime.utcnow()
    ).order_by(RefreshToken.created_at.desc())

    result = await db.execute(stmt)
    existing_token = result.scalars().first()

    if existing_token:
        return existing_token.token

    refresh_token_str = secrets.token_urlsafe(64)

    refresh_token = RefreshToken(
        id=uuid4(),
        user_id=user.id,
        token=refresh_token_str,
        created_at=datetime.utcnow(),
        expires_at=datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        revoked_at=None
    )

    db.add(refresh_token)
    await db.commit()
    await db.refresh(refresh_token)

    return refresh_token.token


async def generate_tokens(user: User, db: AsyncSession):
    access_token, expire = create_access_token({"sub": str(user.id)})
    refresh_token = await get_or_create_refresh_token(user, db)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "expires_at": expire.isoformat()
    }
