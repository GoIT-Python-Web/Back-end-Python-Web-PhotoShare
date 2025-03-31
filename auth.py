

from fastapi import APIRouter, Body, Depends, HTTPException, status, Security, Request, BackgroundTasks, Form


from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.database.db import get_db
from src.entity.models import User


async def get_current_user(email: str, db: AsyncSession = Depends(get_db)) -> User | None:
    query = select(User).filter_by(email=email)
    user = await db.execute(query)
    return user.scalar_one_or_none()