import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from datetime import datetime, timezone
from src.entity.models import User
from src.repositories.admin_search_repository import get_user_by_id, search_users
from src.schemas.admin_search import UserSearchRequest

@pytest.mark.asyncio
async def test_get_user_by_id_found():
    test_user_id = uuid4()
    mock_user = User(
        id=test_user_id,
        username="test",
        email="test@example.com",
        name="Test",
        type="user",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )

    mock_scalars = MagicMock()
    mock_scalars.first.return_value = mock_user

    mock_result = MagicMock()
    mock_result.scalars.return_value = mock_scalars

    mock_session = AsyncMock()
    mock_session.execute.return_value = mock_result

    result = await get_user_by_id(test_user_id, mock_session)
    assert result == mock_user


@pytest.mark.asyncio
async def test_get_user_by_id_not_found():
    test_user_id = uuid4()

    mock_scalars = MagicMock()
    mock_scalars.first.return_value = None

    mock_result = MagicMock()
    mock_result.scalars.return_value = mock_scalars

    mock_session = AsyncMock()
    mock_session.execute.return_value = mock_result

    result = await get_user_by_id(test_user_id, mock_session)
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

    mock_scalars = MagicMock()
    mock_scalars.all.return_value = [mock_user]

    mock_result = MagicMock()
    mock_result.scalars.return_value = mock_scalars

    mock_session = AsyncMock()
    mock_session.execute.return_value = mock_result

    filters = UserSearchRequest(search="test")

    result = await search_users(
        db=mock_session,
        filters=filters,
        current_user_is_admin=True
    )

    assert result == [mock_user]