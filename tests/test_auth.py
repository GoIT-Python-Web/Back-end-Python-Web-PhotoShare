import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from fastapi import HTTPException
from fastapi.testclient import TestClient

from src.entity.models import User, RefreshToken
from src.schemas.user_schema import UserLogin, UserCreate
from src.services.auth_service import AuthService
from src.services.token_service import TokenService
from main import app


@pytest.fixture
def fake_db():
    return MagicMock()


@pytest.fixture
def user_data():
    return UserCreate(email="test@example.com", password="testpassword", username="testuser")


@pytest.fixture
def user_login():
    return UserLogin(email="test@example.com", password="testpassword")


@pytest.fixture
def test_user():
    return User(id=uuid4(), email="test@example.com", username="testuser", hashed_password="hashed", is_active=True)


@pytest.fixture
def test_token():
    return "access-token"


@pytest.fixture
def test_refresh_token():
    return "refresh-token"


@pytest.fixture
def client():
    return TestClient(app)


# ========== AuthService ==========

@pytest.mark.asyncio
async def test_register_user(fake_db, user_data, monkeypatch):
    monkeypatch.setattr("src.services.auth_service.get_password_hash", lambda x: "hashed")
    monkeypatch.setattr("src.services.auth_service.create_access_token", lambda data: "access-token")
    monkeypatch.setattr("src.services.auth_service.create_refresh_token", lambda: "refresh-token")

    fake_db.execute = AsyncMock()
    fake_db.commit = AsyncMock()
    fake_db.refresh = AsyncMock()

    service = AuthService(fake_db)
    result = await service.register(user_data)
    assert result["access_token"] == "access-token"
    assert result["refresh_token"] == "refresh-token"


@pytest.mark.asyncio
async def test_login_user_success(fake_db, user_login, test_user, monkeypatch):
    monkeypatch.setattr("src.services.auth_service.verify_password", lambda raw, hashed: True)
    monkeypatch.setattr("src.services.auth_service.create_access_token", lambda data: "access-token")
    monkeypatch.setattr("src.services.auth_service.create_refresh_token", lambda: "refresh-token")

    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = test_user
    fake_db.execute = AsyncMock(return_value=result_mock)

    service = AuthService(fake_db)
    tokens = await service.login(user_login)
    assert tokens["access_token"] == "access-token"
    assert tokens["refresh_token"] == "refresh-token"


@pytest.mark.asyncio
async def test_login_user_wrong_password(fake_db, user_login, test_user, monkeypatch):
    monkeypatch.setattr("src.services.auth_service.verify_password", lambda raw, hashed: False)

    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = test_user
    fake_db.execute = AsyncMock(return_value=result_mock)

    service = AuthService(fake_db)
    with pytest.raises(HTTPException) as exc:
        await service.login(user_login)
    assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_refresh_token_success(fake_db, test_user, monkeypatch):
    monkeypatch.setattr("src.services.token_service.decode_refresh_token", lambda token: {"sub": str(test_user.id)})
    monkeypatch.setattr("src.services.token_service.create_access_token", lambda data: "new-access-token")

    token_service = TokenService(fake_db)
    token = await token_service.refresh("valid-refresh-token")
    assert token == "new-access-token"


@pytest.mark.asyncio
async def test_refresh_token_invalid(monkeypatch):
    monkeypatch.setattr("src.services.token_service.decode_refresh_token", lambda token: None)

    token_service = TokenService(fake_db=MagicMock())
    with pytest.raises(HTTPException) as exc:
        await token_service.refresh("invalid-token")
    assert exc.value.status_code == 401


# ========== ROUTES (Integration tests) ==========

def test_register_route(client, monkeypatch):
    monkeypatch.setattr("src.api.auth.get_auth_service", lambda: AsyncMock(
        register=AsyncMock(return_value={"access_token": "test", "refresh_token": "test"})))

    response = client.post("/auth/register", json={
        "email": "user@example.com",
        "username": "user1",
        "password": "password"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_route(client, monkeypatch):
    monkeypatch.setattr("src.api.auth.get_auth_service", lambda: AsyncMock(
        login=AsyncMock(return_value={"access_token": "test", "refresh_token": "test"})))

    response = client.post("/auth/login", json={
        "email": "user@example.com",
        "password": "password"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_refresh_route(client, monkeypatch):
    monkeypatch.setattr("src.api.auth.get_token_service", lambda: AsyncMock(
        refresh=AsyncMock(return_value="new-access-token")))

    response = client.post("/auth/refresh", headers={"Authorization": "Bearer some-refresh-token"})
    assert response.status_code == 200
    assert response.json()["access_token"] == "new-access-token"





