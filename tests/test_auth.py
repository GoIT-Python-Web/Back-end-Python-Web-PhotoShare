import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from datetime import datetime, timedelta

from fastapi import HTTPException
from src.entity.models import User, UserTypeEnum, RefreshToken
from src.schemas.user_schema import UserCreate, UserLogin
from src.services.auth_service import generate_tokens


@pytest.fixture
def fake_db():
    return MagicMock()


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


# ========== Register Route Tests ==========

@pytest.mark.asyncio
async def test_register_first_user(fake_db, user_create):
    fake_db.execute = AsyncMock(return_value=MagicMock(scalars=MagicMock(return_value=MagicMock(first=MagicMock(return_value=None)))))
    fake_db.commit = AsyncMock()
    fake_db.refresh = AsyncMock()

    from src.repositories.user_repository import create_user
    from src.repositories.user_repository import get_user_by_email
    from src.routes.auth import register
    create_user = AsyncMock(return_value={"email": user_create.email, "username": user_create.username})
    get_user_by_email = AsyncMock(return_value=None)

    response = await register(user_create, fake_db)
    assert response == "You're welcome" 


#@pytest.mark.asyncio
#async def test_register_email_exists(fake_db, user_create, existing_user):
    #from src.repositories.user_repository import create_user
    #from src.repositories.user_repository import get_user_by_email
    #from src.routes.auth import register
    
    # Мокуємо асинхронну функцію get_user_by_email, щоб вона повернула existing_user
    #get_user_by_email = AsyncMock(return_value=existing_user)
    
    # Мокуємо create_user, якщо потрібно
    #create_user = AsyncMock()

    #with pytest.raises(HTTPException) as e:
        # Викликаємо асинхронну функцію register
        #await register(user_create, fake_db)
    
    #assert e.value.status_code == 400
    #assert e.value.detail == "Email already registered"



# ========== Login Route Tests ==========

#@pytest.mark.asyncio
#async def test_login_success(fake_db, db_user):
    #from src.services.auth_service import verify_password
    #from src.repositories.user_repository import get_user_by_email
    #from src.routes.auth import login
    #get_user_by_username = AsyncMock(return_value=db_user)
    #verify_password = AsyncMock(return_value=True)
    #generate_tokens = AsyncMock(return_value={"access_token": "token", "refresh_token": "refresh", "expires_at": datetime.utcnow().isoformat()})

    #user_login = UserLogin(username="loginuser", password="securepassword")
    #response = await login(user_login, fake_db)
    #assert "access_token" in response


#@pytest.mark.asyncio
#async def test_login_invalid_credentials(fake_db, monkeypatch):
    #from src.routes import auth
    #from src.schemas.user_schema import UserLogin
    #from fastapi import HTTPException

    # Замінюємо справжню функцію на мокану
    #monkeypatch.setattr("src.routes.auth.get_user_by_username", AsyncMock(return_value=None))

    #user_login = UserLogin(username="wrong", password="wrong")
    
    #with pytest.raises(HTTPException) as e:
        #await auth.login(user_login, fake_db)

    #assert e.value.status_code == 400
    #assert e.value.detail == "Invalid credentials"



# ========== Logout Route Tests ==========

@pytest.mark.asyncio
async def test_logout_success(fake_db, refresh_token_obj):
    from src.routes.auth import logout
    fake_db.execute = AsyncMock(return_value=MagicMock(scalars=MagicMock(return_value=MagicMock(first=MagicMock(return_value=refresh_token_obj)))))
    fake_db.commit = AsyncMock()

    response = await logout(refresh_token="valid_refresh_token", db=fake_db)
    assert response["message"] == "Token revoked successfully"
    assert refresh_token_obj.revoked_at is not None


@pytest.mark.asyncio
async def test_logout_token_not_found(fake_db):
    from src.routes.auth import logout
    fake_db.execute = AsyncMock(return_value=MagicMock(scalars=MagicMock(return_value=MagicMock(first=MagicMock(return_value=None)))))

    with pytest.raises(HTTPException) as e:
        await logout(refresh_token="nonexistent", db=fake_db)
    assert e.value.status_code == 404


# ========== Refresh Token Route Tests ==========

@pytest.mark.asyncio
async def test_refresh_token_success(db_user, fake_db, refresh_token_obj):
    from src.services.auth_service import get_or_create_refresh_token, create_access_token
    fake_db.execute = AsyncMock(return_value=MagicMock(scalars=MagicMock(return_value=MagicMock(first=MagicMock(return_value=refresh_token_obj)))))
    create_access_token = AsyncMock(return_value=("new_token", datetime.utcnow() + timedelta(hours=1)))

    response = await get_or_create_refresh_token(db_user,fake_db)
    assert response == refresh_token_obj.token







#from unittest.mock import AsyncMock
#from fastapi import HTTPException
#from datetime import datetime, timedelta
#from uuid import uuid4
#from src.services.auth_service import get_or_create_refresh_token

#@pytest.mark.asyncio
#async def test_refresh_token_invalid(db_user, fake_db):
    # Мокування асинхронного методу execute
    #fake_db.execute = AsyncMock()

    # Повертаємо результат execute, який містить асинхронний об'єкт scalars
    #fake_db.execute.return_value = AsyncMock(scalars=AsyncMock(return_value=AsyncMock(first=AsyncMock(return_value=None))))

    # Перевіряємо, чи піднімається виключення, якщо токен не знайдений
    #with pytest.raises(HTTPException) as e:
        #await get_or_create_refresh_token(db_user, fake_db)

    # Перевіряємо, чи було піднято виключення 401 і правильне повідомлення
    #assert e.value.status_code == 401
    #assert e.value.detail == "Unauthorized"
