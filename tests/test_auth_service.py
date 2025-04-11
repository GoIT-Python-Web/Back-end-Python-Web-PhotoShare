import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timedelta
from uuid import uuid4
from src.entity.models import User, RefreshToken
from src.services.auth_service import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_or_create_refresh_token,
    generate_tokens
)
from fastapi import HTTPException
from src.entity.models import UserTypeEnum
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



from unittest.mock import AsyncMock, MagicMock
from src.services.auth_service import get_or_create_refresh_token
from src.entity.models import User, RefreshToken
from datetime import datetime, timedelta

#@pytest.mark.asyncio
#async def test_get_or_create_refresh_token(db_user, fake_db):
    # Мокування результату виконання SQL запиту
    #mock_result = MagicMock()
    # Мокування асинхронного виконання
    #mock_result.scalars.return_value.first.return_value = None  # Для випадку, коли токен не знайдений

    # Мокування методу execute
    #fake_db.execute = AsyncMock(return_value=mock_result)

    # Викликаємо функцію для створення нового токену поновлення
    #refresh_token = await get_or_create_refresh_token(db_user, fake_db)

    # Перевірка, що токен поновлення був створений
    #assert isinstance(refresh_token, str)  # Токен має бути рядком



#@pytest.mark.asyncio
#async def test_generate_tokens(db_user, fake_db):
    # Мокування створення токену доступу
    #create_access_token = AsyncMock(return_value=("access_token_str", datetime.utcnow() + timedelta(hours=1)))
    
    # Мокування get_or_create_refresh_token
    #fake_db.execute = AsyncMock(return_value=MagicMock(scalars=AsyncMock(return_value=AsyncMock(first=AsyncMock(return_value=None)))))
    #refresh_token = "refresh_token_str"

    # Викликаємо функцію generate_tokens
    #response = await generate_tokens(db_user, fake_db)

    # Перевірка результатів
    #assert "access_token" in response
    #assert "refresh_token" in response
    #assert "expires_at" in response
    #assert isinstance(response["access_token"], str)
    #assert isinstance(response["refresh_token"], str)
    #assert isinstance(response["expires_at"], str)  # Перевірка, що expire — це строковий ISO формат
