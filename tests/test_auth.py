from httpx import AsyncClient
import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from datetime import datetime, timedelta
from fastapi import HTTPException
from src.entity.models import User, UserTypeEnum, RefreshToken
from src.schemas.user_schema import UserCreate, UserLogin
from src.services.auth_service import generate_tokens
from fastapi.testclient import TestClient
from fastapi import Request, APIRouter
from main import app
from src.entity.models import RefreshToken, UserTypeEnum, User


client = TestClient(app)
router = APIRouter()

@pytest.fixture
def fake_db():
    return MagicMock()


def fake_request():
    with client as c:
        req = Request(scope={"type": "http"})
        return req

@pytest.fixture
def user_create():
    return UserCreate(
        name="New User",
        email="new@example.com",
        password="securepassword",
        username="newuser"
    )


@pytest.fixture
def existing_user():
    return User(
        id=uuid4(),
        email="existing@example.com",
        password="hashedpassword",
        username="existinguser",
        is_active=True,
        type=UserTypeEnum.user
    )


@pytest.fixture
def first_user():
    return None  # Simulates no user in DB for first registration


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
def refresh_token_obj(db_user):
    return RefreshToken(
        id=uuid4(),
        token="valid_refresh_token",
        user_id=db_user.id,
        revoked_at=None,
        expires_at=datetime.utcnow() + timedelta(days=7)
    )



@pytest.mark.asyncio
async def test_register_first_user_integration():
    payload = {
        "name": f"new{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "email": f"new{datetime.now().strftime('%Y%m%d%H%M%S')}@example.com",
        "password": "securepassword",
        "username": f"new{datetime.now().strftime('%Y%m%d%H%M%S')}"
    }

    response = client.post("/register", json=payload)

    print("STATUS:", response.status_code)
    print("TEXT:", response.text)

    assert response.status_code == 200
    data = response.json()
    assert data == "You're welcome"


client = TestClient(app)

def test_logout_no_token():
    response = client.post("/logout")
    assert response.status_code == 401  # бо токен не передано


@pytest.mark.asyncio
async def test_refresh_token_success(db_user, fake_db, refresh_token_obj):
    from src.services.auth_service import get_or_create_refresh_token, create_access_token
    fake_db.execute = AsyncMock(return_value=MagicMock(scalars=MagicMock(return_value=MagicMock(first=MagicMock(return_value=refresh_token_obj)))))
    create_access_token = AsyncMock(return_value=("new_token", datetime.utcnow() + timedelta(hours=1)))

    response = await get_or_create_refresh_token(db_user,fake_db)
    assert response == refresh_token_obj.token


