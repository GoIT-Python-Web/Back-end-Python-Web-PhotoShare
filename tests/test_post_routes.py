import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from fastapi import HTTPException
from src.repositories.post_repository import PostRepository
from src.services.post_service import PostService
from src.schemas.post import PostCreateModel, PostCreateResponse
from src.entity.models import Post, PostRating, User
from datetime import datetime
from io import BytesIO
from src.entity.models import User, UserTypeEnum
from unittest.mock import AsyncMock, patch

@pytest.fixture
def fake_db():
    return MagicMock()

@pytest.fixture
def current_user():
    return User(id=uuid4(), email="test@example.com", is_active=True)

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

@patch("src.repositories.post_repository.Post", autospec=True)
@pytest.mark.asyncio
async def test_create_post_success(mock_post_class, fake_db, current_user):
    fake_post_id = uuid4()
    mock_post_instance = MagicMock()
    mock_post_instance.id = fake_post_id
    mock_post_instance.title = "Test Post"
    mock_post_instance.image_url = "img_url"
    mock_post_instance.user_id = current_user.id

    mock_post_class.return_value = mock_post_instance

    post_data = PostCreateModel(
        title="Test Post",
        description="A test post",
        image_url="img_url",
        location="Test City",
        tags=[{"name": "tag1"}]
    )

    fake_db.execute = AsyncMock()
    fake_db.commit = AsyncMock()
    fake_db.flush = AsyncMock()
    fake_db.refresh = AsyncMock()

    repo = PostRepository(fake_db, current_user)
    service = PostService(repo)
    service.post_repo.get_post = AsyncMock(return_value=mock_post_instance)

    result = await service.create_post(post_data)

    assert isinstance(result, PostCreateResponse)
    assert result.id == fake_post_id
    assert result.image_url == "img_url"

@pytest.mark.asyncio
async def test_get_all_posts(fake_db, sample_post):
    result_mock = MagicMock()
    scalars_mock = MagicMock()
    scalars_mock.all.return_value = [sample_post]
    result_mock.scalars.return_value = scalars_mock
    fake_db.execute = AsyncMock(return_value=result_mock)

    service = PostService(PostRepository(fake_db))
    posts = await service.get_all_posts()
    
    assert len(posts) == 1
    assert posts[0].title == "Sample Title"

@pytest.mark.asyncio
async def test_get_post_by_id_found(fake_db, sample_post):
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = sample_post
    fake_db.execute = AsyncMock(return_value=result_mock)

    service = PostService(PostRepository(fake_db))
    post = await service.get_post_by_id(sample_post.id)

    assert post.id == sample_post.id
    assert post.title == "Sample Title"

@pytest.mark.asyncio
async def test_get_post_by_id_not_found(fake_db):
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = None
    fake_db.execute = AsyncMock(return_value=result_mock)

    service = PostService(PostRepository(fake_db))
    with pytest.raises(HTTPException) as e:
        await service.get_post_by_id(uuid4())
    assert e.value.status_code == 404

@pytest.mark.asyncio
async def test_update_post_success(fake_db, sample_post, current_user):
    fake_db.execute = AsyncMock()

    updated_post = sample_post
    updated_post.description = "Updated description"

    fake_db.execute.side_effect = [
        MagicMock(),
        MagicMock(scalar_one_or_none=MagicMock(return_value=updated_post))  # for SELECT
    ]

    fake_db.commit = AsyncMock()
    fake_db.refresh = AsyncMock()

    service = PostService(PostRepository(fake_db, current_user))
    result = await service.update_post(sample_post.id, "Updated description")

    assert result.description == "Updated description"
    fake_db.commit.assert_awaited_once()

@pytest.mark.asyncio
async def test_update_post_not_found(fake_db, current_user):
    result_mock = MagicMock()
    result_mock.scalar_one_or_none = MagicMock(return_value=None)
    fake_db.execute = AsyncMock(return_value=result_mock)
    fake_db.commit = AsyncMock()

    service = PostService(PostRepository(fake_db, current_user))

    with pytest.raises(HTTPException) as exc_info:
        await service.update_post(uuid4(), "New text")

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Post not found"

@pytest.mark.asyncio
async def test_delete_post_success(fake_db, sample_post, current_user):
    fake_db.execute = AsyncMock(return_value=MagicMock(rowcount=1))
    fake_db.commit = AsyncMock()
    fake_db.delete = AsyncMock()

    service = PostService(PostRepository(fake_db, current_user))
    result = await service.delete_post(sample_post.id)

    assert result is True

@pytest.mark.asyncio
async def test_delete_post_not_found(fake_db, current_user):
    fake_db.execute = AsyncMock(return_value=MagicMock(rowcount=0))
    fake_db.commit = AsyncMock()

    service = PostService(PostRepository(fake_db, current_user))
    result = await service.delete_post(uuid4())
    assert result is False
