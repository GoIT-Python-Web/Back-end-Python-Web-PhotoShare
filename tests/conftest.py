import pytest
from main import app
from uuid import uuid4
from datetime import datetime
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock
from src.entity.models import User, Comment, UserTypeEnum
from src.schemas.user_schema import UserLogin, UserCreate
from src.entity.models import Post, PostRating, User




@pytest.fixture
def fake_db():
    db = MagicMock()
    db.get = AsyncMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    db.execute = AsyncMock()
    return db


@pytest.fixture
def admin_user():
    return User(
        id=uuid4(), 
        email="admin@example.com", 
        type=UserTypeEnum.admin, 
        is_active=True
    )


@pytest.fixture
def user_instance():
    return User(
        id=uuid4(), 
        username="user123",
        email="user@example.com", 
        type=UserTypeEnum.user, 
        is_active=True,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )


@pytest.fixture
def banned_user():
    return User(
        id=uuid4(), 
        email="banned@example.com", 
        type=UserTypeEnum.user, 
        is_active=False
    )


@pytest.fixture
def comment_instance():
    return Comment(
        id=uuid4(), 
        post_id=uuid4(), 
        is_deleted=False
    )


@pytest.fixture
def user_data():
    return UserCreate(
        email="test@example.com", 
        password="testpassword", 
        username="testuser"
    )


@pytest.fixture
def user_login():
    return UserLogin(
        email="test@example.com", 
        password="testpassword"
    )


@pytest.fixture
def test_token():
    return "access-token"


@pytest.fixture
def test_refresh_token():
    return "refresh-token"


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def current_user():
    return User(
        id=uuid4(), 
        email="test@example.com", 
        is_active=True
    )


@pytest.fixture
def sample_post(current_user):
    return Post(
        id=uuid4(),
        user_id=current_user.id,
        title="Sample Title",
        description="Sample Description",
        image_url="http://test.com/image.jpg",
        location="Moon",
        created_at=datetime.now(),
        updated_at=datetime.now(),
        tags=[],
        ratings=[
            PostRating(rating=4),
            PostRating(rating=5),
        ],
        user=current_user
    )


@pytest.fixture
def test_user():
    return User(
        id=uuid4(),
        email="user@example.com",
        username="testuser",
        is_active=True,
        type=UserTypeEnum.user,
    )