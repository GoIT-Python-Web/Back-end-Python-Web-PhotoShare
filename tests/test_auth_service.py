import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timedelta
from uuid import uuid4
from src.entity.models import User, RefreshToken
from fastapi import HTTPException
from src.entity.models import UserTypeEnum
from src.services.auth_service import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_or_create_refresh_token,
    generate_tokens
)

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

@pytest.fixture
def fake_db():
    return MagicMock()


@pytest.mark.parametrize("password, hashed_password", [
    ("0000", "$2b$12$iNh9wtyHQcUBCWgZs8vDg.GrIz42J9PAQxRVtVl1RwOeYLe7B4PAW"),  # Тут має бути хеш пароля
])
def test_get_password_hash(password, hashed_password):
    hashed = get_password_hash(password)
    assert hashed != password  # Перевірка, що хешовані паролі різні
    assert hashed.startswith("$2b$12$")  # Перевірка, що це bcrypt хеш


def test_verify_password():
    # Мокування хешованого пароля
    password = "0000"
    hashed_password = "$2b$12$iNh9wtyHQcUBCWgZs8vDg.GrIz42J9PAQxRVtVl1RwOeYLe7B4PAW"  # Тут повинен бути реальний хеш
    assert verify_password(password, hashed_password)  # Перевірка, що пароль збігається з хешем


@pytest.mark.parametrize("data, expires_delta", [
    ({"sub": "user_id"}, timedelta(minutes=15)),
])
def test_create_access_token(data, expires_delta):
    token, expire = create_access_token(data, expires_delta)
    assert isinstance(token, str)  # Перевірка, що токен є рядком
    assert isinstance(expire, datetime)  # Перевірка, що expire є datetime
    assert expire > datetime.utcnow()  # Перевірка, що час завершення більший за поточний



