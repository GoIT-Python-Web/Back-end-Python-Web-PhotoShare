from datetime import timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, asc, desc, cast, Date
from src.entity.models import User
from typing import List
from src.schemas.admin_search import UserSearchRequest

async def search_users(
    db: AsyncSession,
    filters: UserSearchRequest,
    current_user_is_admin: bool = False,
) -> List[User]:
    stmt = select(User)
    conditions = []

    if filters.search:
        words = [word.strip() for word in filters.search.split(',') if word.strip()]
        word_conditions = [
            or_(
                User.name.ilike(f"%{word}%"),
                User.email.ilike(f"%{word}%")
            ) for word in words
        ]
        conditions.append(or_(*word_conditions))

    if filters.role:
        conditions.append(User.type == filters.role)

    if not current_user_is_admin:
        conditions.append(User.is_active == True)

    if filters.reg_date_from and filters.reg_date_to:
        reg_date_to = filters.reg_date_to + timedelta(days=1)
        conditions.append(User.created_at.between(filters.reg_date_from, reg_date_to))
    elif filters.reg_date_from:
        conditions.append(cast(User.created_at, Date) == filters.reg_date_from.date())
    elif filters.reg_date_to:
        conditions.append(cast(User.created_at, Date) == filters.reg_date_to.date())

    if conditions:
        stmt = stmt.where(and_(*conditions))

    sort_column = {
        "name": User.name,
        "registration_date": User.created_at
    }.get(filters.sort_by, User.name)

    if filters.sort_order == "desc":
        stmt = stmt.order_by(desc(sort_column))
    else:
        stmt = stmt.order_by(asc(sort_column))

    result = await db.execute(stmt)
    return result.scalars().all()