import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from datetime import datetime
from src.entity.models import Comment, User, Post
from src.services.comment_service import CommentService
from src.schemas.comment import CommentCreateDTO, CommentUpdateDTO
from fastapi import HTTPException


@pytest.mark.asyncio
async def test_add_comment_success():
    user_id = uuid4()
    post_id = uuid4()
    dto = CommentCreateDTO(message="Hello world")

    mock_comment = Comment(
        id=uuid4(),
        user_id=user_id,
        post_id=post_id,
        message=dto.message,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        is_deleted=False
    )

    mock_repo = MagicMock()
    mock_repo.create = AsyncMock(return_value=mock_comment)

    service = CommentService(mock_repo)
    result = await service.add_comment(user_id, post_id, dto)

    assert isinstance(result, Comment)
    assert result.message == "Hello world"
    assert result.user_id == user_id
    assert result.post_id == post_id


@pytest.mark.asyncio
async def test_get_comment_success():
    comment_id = uuid4()
    mock_comment = Comment(id=comment_id, user_id=uuid4(), post_id=uuid4(), message="Test", is_deleted=False)

    mock_repo = MagicMock()
    mock_repo.get_by_id = AsyncMock(return_value=mock_comment)

    service = CommentService(mock_repo)
    result = await service.get_comment(comment_id)

    assert result.id == comment_id
    assert result.message == "Test"


@pytest.mark.asyncio
async def test_get_comment_not_found():
    mock_repo = MagicMock()
    mock_repo.get_by_id = AsyncMock(return_value=None)

    service = CommentService(mock_repo)

    with pytest.raises(HTTPException) as exc_info:
        await service.get_comment(uuid4())

    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_update_comment_success():
    comment_id = uuid4()
    user_id = uuid4()
    dto = CommentUpdateDTO(message="Updated")

    mock_comment = Comment(id=comment_id, user_id=user_id, post_id=uuid4(), message="Old", is_deleted=False)

    mock_repo = MagicMock()
    mock_repo.get_by_id = AsyncMock(return_value=mock_comment)
    mock_repo.update = AsyncMock(return_value=mock_comment)

    service = CommentService(mock_repo)
    result = await service.update_comment(comment_id, dto, User(id=user_id))

    assert result.id == comment_id
    assert result.user_id == user_id


@pytest.mark.asyncio
async def test_update_comment_unauthorized():
    comment_id = uuid4()
    dto = CommentUpdateDTO(message="Updated")

    mock_comment = Comment(id=comment_id, user_id=uuid4(), post_id=uuid4(), message="Old")

    mock_repo = MagicMock()
    mock_repo.get_by_id = AsyncMock(return_value=mock_comment)

    service = CommentService(mock_repo)
    with pytest.raises(HTTPException) as exc_info:
        await service.update_comment(comment_id, dto, User(id=uuid4()))

    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_delete_comment_success():
    comment_id = uuid4()
    user_id = uuid4()

    mock_comment = Comment(id=comment_id, user_id=user_id, post_id=uuid4(), message="Hello")

    mock_repo = MagicMock()
    mock_repo.get_by_id = AsyncMock(return_value=mock_comment)
    mock_repo.delete = AsyncMock(return_value=True)

    service = CommentService(mock_repo)
    result = await service.delete_comment(comment_id, User(id=user_id))

    assert result is True


@pytest.mark.asyncio
async def test_delete_comment_unauthorized():
    comment_id = uuid4()

    mock_comment = Comment(id=comment_id, user_id=uuid4(), post_id=uuid4(), message="Hello")

    mock_repo = MagicMock()
    mock_repo.get_by_id = AsyncMock(return_value=mock_comment)

    service = CommentService(mock_repo)
    with pytest.raises(HTTPException) as exc_info:
        await service.delete_comment(comment_id, User(id=uuid4()))

    assert exc_info.value.status_code == 404