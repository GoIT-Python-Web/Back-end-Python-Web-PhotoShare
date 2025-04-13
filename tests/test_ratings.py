import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from src.entity.models import User, Post, PostRating
from src.repositories.rating_repository import add_rating, get_rating_data
from fastapi import HTTPException


@pytest.mark.asyncio
async def test_add_rating_success():
    post_id = uuid4()
    user_id = uuid4()

    mock_post = Post(id=post_id, user_id=uuid4())
    mock_user = User(id=user_id)

    mock_scalars_post = MagicMock()
    mock_scalars_post.first.return_value = mock_post

    mock_scalars_rating = MagicMock()
    mock_scalars_rating.first.return_value = None

    mock_result_post = MagicMock()
    mock_result_post.scalars.return_value = mock_scalars_post

    mock_result_rating = MagicMock()
    mock_result_rating.scalars.return_value = mock_scalars_rating

    mock_session = AsyncMock()
    mock_session.execute.side_effect = [mock_result_post, mock_result_rating]
    mock_session.commit = AsyncMock()
    mock_session.refresh = AsyncMock()

    result = await add_rating(post_id, 5, mock_session, mock_user)
    assert isinstance(result, PostRating)
    assert result.rating == 5


@pytest.mark.asyncio
async def test_get_rating_data():
    post_id = uuid4()
    mock_post = Post(id=post_id)

    mock_scalars_post = MagicMock()
    mock_scalars_post.first.return_value = mock_post

    mock_result_post = MagicMock()
    mock_result_post.scalars.return_value = mock_scalars_post

    mock_result_rating_data = MagicMock()
    mock_result_rating_data.first.return_value = (4.5, 10)

    mock_session = AsyncMock()
    mock_session.execute.side_effect = [mock_result_post, mock_result_rating_data]

    avg, count = await get_rating_data(post_id, mock_session)
    assert avg == 4.5
    assert count == 10


@pytest.mark.asyncio
async def test_get_rating_data_no_ratings():
    post_id = uuid4()
    mock_post = Post(id=post_id)

    mock_scalars_post = MagicMock()
    mock_scalars_post.first.return_value = mock_post

    mock_result_post = MagicMock()
    mock_result_post.scalars.return_value = mock_scalars_post

    mock_result_rating_data = MagicMock()
    mock_result_rating_data.first.return_value = (None, 0)

    mock_session = AsyncMock()
    mock_session.execute.side_effect = [mock_result_post, mock_result_rating_data]

    avg, count = await get_rating_data(post_id, mock_session)
    assert avg == 0
    assert count == 0