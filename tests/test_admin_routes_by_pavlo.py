import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from fastapi import HTTPException
from src.entity.models import User, Comment, UserTypeEnum
from src.services.admin_user_service import AdminUserService
from src.services.admin_comment_service import AdminCommentService


@pytest.fixture
def fake_db():
    return MagicMock()


@pytest.fixture
def admin_user():
    return User(id=uuid4(), email="admin@example.com", type=UserTypeEnum.admin, is_active=True)


@pytest.fixture
def user_instance():
    return User(id=uuid4(), email="user@example.com", type=UserTypeEnum.user, is_active=True, username="user123")


@pytest.fixture
def banned_user():
    return User(id=uuid4(), email="banned@example.com", type=UserTypeEnum.user, is_active=False)


@pytest.fixture
def comment_instance():
    return Comment(id=uuid4(), post_id=uuid4(), is_deleted=False)


# ========== AdminUserService Tests ==========

@pytest.mark.asyncio
async def test_admin_get_all_users(fake_db, user_instance):
    result_mock = MagicMock()
    scalars_mock = MagicMock()
    scalars_mock.all.return_value = [user_instance]
    result_mock.scalars.return_value = scalars_mock
    fake_db.execute = AsyncMock(return_value=result_mock)

    service = AdminUserService(fake_db)
    users = await service.admin_get_all_users()
    assert len(users) == 1
    assert users[0].email == user_instance.email


@pytest.mark.asyncio
async def test_admin_ban_user_success(fake_db, admin_user, user_instance):
    fake_db.get = AsyncMock(return_value=user_instance)
    fake_db.commit = AsyncMock(return_value=None)
    fake_db.refresh = AsyncMock(return_value=None)
    service = AdminUserService(fake_db)
    result = await service.admin_ban_user(user_instance.id, admin_user)
    assert result["message"] == f"User {user_instance.email} has been banned successfully"


@pytest.mark.asyncio
async def test_admin_ban_user_already_banned(fake_db, admin_user, banned_user):
    fake_db.get = AsyncMock(return_value=banned_user)
    service = AdminUserService(fake_db)
    with pytest.raises(HTTPException) as e:
        await service.admin_ban_user(banned_user.id, admin_user)
    assert e.value.status_code == 400


@pytest.mark.asyncio
async def test_admin_ban_user_admin_target(fake_db, admin_user):
    fake_db.get = AsyncMock(return_value=admin_user)
    service = AdminUserService(fake_db)
    with pytest.raises(HTTPException) as e:
        await service.admin_ban_user(admin_user.id, admin_user)
    assert e.value.status_code == 403


@pytest.mark.asyncio
async def test_admin_ban_user_not_found(fake_db, admin_user):
    fake_db.get = AsyncMock(return_value=None)
    service = AdminUserService(fake_db)
    with pytest.raises(HTTPException) as e:
        await service.admin_ban_user(uuid4(), admin_user)
    assert e.value.status_code == 404


@pytest.mark.asyncio
async def test_admin_toggle_user_role_user_to_admin(fake_db, user_instance):
    fake_db.get = AsyncMock(return_value=user_instance)
    fake_db.commit = AsyncMock(return_value=None)
    fake_db.refresh = AsyncMock(return_value=None)
    service = AdminUserService(fake_db)
    result = await service.admin_toggle_user_role(user_instance.id)
    assert result["new_role"] == UserTypeEnum.admin
    assert result["id"] == user_instance.id


@pytest.mark.asyncio
async def test_admin_toggle_user_role_admin_to_user(fake_db, admin_user):
    fake_db.get = AsyncMock(return_value=admin_user)
    fake_db.commit = AsyncMock(return_value=None)
    fake_db.refresh = AsyncMock(return_value=None)
    service = AdminUserService(fake_db)
    result = await service.admin_toggle_user_role(admin_user.id)
    assert result["new_role"] == UserTypeEnum.user


@pytest.mark.asyncio
async def test_admin_toggle_user_role_user_not_found(fake_db):
    fake_db.get = AsyncMock(return_value=None)
    service = AdminUserService(fake_db)
    with pytest.raises(HTTPException) as e:
        await service.admin_toggle_user_role(uuid4())
    assert e.value.status_code == 404


# ========== AdminCommentService Tests ==========

@pytest.mark.asyncio
async def test_admin_soft_delete_comment_success(fake_db, comment_instance):
    fake_db.get = AsyncMock(return_value=comment_instance)
    fake_db.commit = AsyncMock(return_value=None)
    service = AdminCommentService(fake_db)
    result = await service.admin_soft_delete_comment(comment_instance.id)
    assert result["message"] == "Comment marked as deleted"
    assert comment_instance.is_deleted is True


@pytest.mark.asyncio
async def test_admin_soft_delete_comment_not_found(fake_db):
    fake_db.get = AsyncMock(return_value=None)
    fake_db.commit = AsyncMock(return_value=None)
    service = AdminCommentService(fake_db)
    with pytest.raises(HTTPException) as e:
        await service.admin_soft_delete_comment(uuid4())
    assert e.value.status_code == 404


@pytest.mark.asyncio
async def test_admin_get_post_comments(fake_db, comment_instance):
    result_mock = MagicMock()
    scalars_mock = MagicMock()
    scalars_mock.all.return_value = [comment_instance]
    result_mock.scalars.return_value = scalars_mock
    fake_db.execute = AsyncMock(return_value=result_mock)

    service = AdminCommentService(fake_db)
    result = await service.admin_get_post_comments(comment_instance.post_id)
    assert len(result) == 1
    assert result[0] == comment_instance



# How to run the tests?  —  pytest tests/test_admin_routes_by_pavlo.py
# Coverage level?  —  pytest --cov=src --cov-report=term-missing
