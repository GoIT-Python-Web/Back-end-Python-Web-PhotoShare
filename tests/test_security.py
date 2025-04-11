import pytest
from unittest.mock import MagicMock
from fastapi import HTTPException
from src.core.security import get_current_user
from src.entity.models import User
from uuid import uuid4
from src.entity.models import UserTypeEnum
from fastapi import HTTPException
from jose import JWTError
from datetime import datetime, timedelta
from src.conf.config import settings
from jose import jwt
from unittest.mock import AsyncMock

@pytest.fixture
def fake_db():
    db = MagicMock()
    db.execute = AsyncMock()
    return db

@pytest.fixture
def db_user():
    return User(
        id=uuid4(),
        email="login@example.com",
        username="loginuser",
        password="$2b$12$hashedvalue",
        is_active=True,
        type=UserTypeEnum.user
    )


@pytest.mark.asyncio
async def test_get_current_user_invalid_token(fake_db):
    # Підроблений або пошкоджений токен
    invalid_token = "this.is.not.a.valid.token"

    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(invalid_token, fake_db)

    assert exc_info.value.status_code == 401
    assert "Invalid token" in str(exc_info.value.detail)

@pytest.mark.asyncio
async def test_get_current_user_missing_sub(fake_db):
    token_data = {"exp": datetime.utcnow() + timedelta(minutes=30)}
    token = jwt.encode(token_data, settings.SECRET_KEY, algorithm="HS256")

    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(token, fake_db)

    assert exc_info.value.status_code == 500
    assert "Missing user ID" in str(exc_info.value.detail)



@pytest.mark.asyncio
async def test_get_current_user_expired_token(fake_db):
    token_data = {"sub": str(uuid4()), "exp": datetime.utcnow() - timedelta(minutes=1)}
    token = jwt.encode(token_data, settings.SECRET_KEY, algorithm="HS256")

    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(token, fake_db)

    assert exc_info.value.status_code == 401
    assert "Token expired" in exc_info.value.detail

@pytest.mark.asyncio
async def test_get_current_user_success(db_user, fake_db):
    # Генерація валідного токену з існуючим user_id
    token_data = {"sub": str(db_user.id), "exp": datetime.utcnow() + timedelta(minutes=30)}
    token = jwt.encode(token_data, settings.SECRET_KEY, algorithm="HS256")

    # Мокаємо відповідь від БД — повертає нашого користувача
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = db_user
    fake_db.execute.return_value = mock_result

    # Викликаємо функцію
    user = await get_current_user(token, fake_db)

    # Перевіряємо, що повернутий користувач правильний
    assert user.id == db_user.id
    assert user.email == db_user.email


@pytest.mark.asyncio
async def test_get_current_user_user_not_found(db_user, fake_db):
    # Генерація валідного токену для користувача
    token_data = {"sub": str(db_user.id), "exp": datetime.utcnow() + timedelta(minutes=30)}
    token = jwt.encode(token_data, settings.SECRET_KEY, algorithm="HS256")

    # Мокаємо відповідь від БД — повертаємо None (користувача не знайдено)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None  # жодного користувача не знайдено
    fake_db.execute.return_value = mock_result

    # Перевірка, що буде піднята помилка
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(token, fake_db)

    assert exc_info.value.status_code == 500
    assert "User not found" in str(exc_info.value.detail)
