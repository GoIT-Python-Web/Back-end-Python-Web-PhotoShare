import pytest
import pytest_asyncio
from uuid import uuid4
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

from src.entity.models import User
from src.schemas.admin_search import UserSearchRequest
from src.repositories.admin_search_repository import get_user_by_id, search_users


@pytest_asyncio.fixture(scope="session", autouse=True)
async def prepare_database():
    yield  # Stub fixture for mock-based tests


@pytest.mark.asyncio
async def test_get_user_by_id_found():
    user_id = uuid4()
    mock_user = User(
        id=user_id,
        username="test",
        email="test@example.com",
        name="Test",
        type="user",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )

    mock_first = MagicMock()
    mock_first.first = AsyncMock(return_value=mock_user)

    mock_session = AsyncMock()
    mock_session.execute.return_value = MagicMock(scalars=MagicMock(return_value=mock_first))

    result = await get_user_by_id(user_id, mock_session)
    assert result == mock_user


@pytest.mark.asyncio
async def test_get_user_by_id_not_found():
    user_id = uuid4()

    mock_first = MagicMock()
    mock_first.first = AsyncMock(return_value=None)

    mock_session = AsyncMock()
    mock_session.execute.return_value = MagicMock(scalars=MagicMock(return_value=mock_first))

    result = await get_user_by_id(user_id, mock_session)
    assert result is None


@pytest.mark.asyncio
async def test_search_users_basic():
    mock_user = User(
        id=uuid4(),
        username="testuser",
        email="test@example.com",
        name="Test User",
        type="user",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )

    mock_all = MagicMock()
    mock_all.all = AsyncMock(return_value=[mock_user])

    mock_session = AsyncMock()
    mock_session.execute.return_value = MagicMock(scalars=MagicMock(return_value=mock_all))

    filters = UserSearchRequest(search="test")

    result = await search_users(
        db=mock_session,
        filters=filters,
        current_user_is_admin=True
    )
    assert result == [mock_user]
