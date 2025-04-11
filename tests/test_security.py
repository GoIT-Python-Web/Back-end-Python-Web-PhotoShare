import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException, status
from jose import jwt
from src.core.security import get_current_user
from src.entity.models import User
from datetime import datetime, timedelta
from uuid import uuid4
from src.entity.models import UserTypeEnum


@pytest.fixture
def fake_db():
    return MagicMock()

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



from fastapi import HTTPException, status
from unittest.mock import MagicMock, AsyncMock
from jose import jwt
from datetime import datetime, timedelta
from src.entity.models import User
from src.conf.config import settings
from uuid import uuid4

@pytest.mark.asyncio
async def test_get_current_user_valid_token(db_user, fake_db):
    # Генерація правильного токену
    token_data = {"sub": str(db_user.id), "exp": datetime.utcnow() + timedelta(minutes=30)}
    token = jwt.encode(token_data, settings.SECRET_KEY, algorithm="HS256")

    # Мокування виконання SQL запиту для користувача
    mock_user = MagicMock(spec=User)
    mock_user.id = db_user.id  # Ставимо правильний id
    mock_user.email = db_user.email  # Ставимо правильну електронну пошту

    fake_db.execute = AsyncMock(return_value=MagicMock(scalars=AsyncMock(return_value=MagicMock(scalar_one_or_none=AsyncMock(return_value=mock_user)))))

    # Викликаємо функцію для отримання користувача
    user = await get_current_user(token, fake_db)

    # Перевірка, що повернений користувач є тим самим, що був переданий
    assert user.id == db_user.id
    assert user.email == db_user.email
