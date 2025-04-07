from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas.post import (
    PostResponse, PostDeleteResponse, PostUpdateResponse, PostModel,
    PostUpdateRequest
)
from uuid import UUID
from src.database.db import get_db
from src.repositories.post_repository import PostRepository
from src.services.post_service import PostService
from typing import List, Optional
from src.entity.models import User
from src.core.dependencies import role_required

router = APIRouter(prefix='/posts', tags=['posts'])

@router.get("/{post_id}", response_model=PostResponse)
async def get_post(
    post_id: UUID, 
    db: AsyncSession = Depends(get_db),
    current_user: User = role_required("user", "admin"), 
):
    service = PostService(PostRepository(current_user, db))
    
    return await service.get_post_by_id(post_id)

@router.get("/", response_model=List[PostResponse])
async def get_posts(
    db: AsyncSession = Depends(get_db), 
    current_user: User = role_required("user", "admin")
):
    service = PostService(PostRepository(current_user, db))
    
    return await service.get_all_posts()

@router.put("/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: UUID, update_data: PostUpdateRequest = Body(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = role_required("user", "admin"),
):
    service = PostService(PostRepository(current_user, db))
    post = await service.get_post_by_id(post_id)

    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    
    if post.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to update this post.",
        )
    
    if not await service.update_post(post_id, update_data.description):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return await service.update_post(post_id, update_data.description)

@router.post("/", response_model=PostResponse)
async def create_post(
    post_data: PostModel, 
    db: AsyncSession = Depends((get_db)),
    current_user: User = role_required("user", "admin")): 
    service = PostService(PostRepository(current_user, db))
    return await service.create_post(post_data.title, post_data.image_url, post_data.description)

@router.delete("/{post_id}", response_model=bool)
async def delete_post(
    post_id: UUID, 
    db: AsyncSession = Depends(get_db),
    current_user: User = role_required("user", "admin"),
):
    service = PostService(PostRepository(current_user, db))
    post = await service.get_post_by_id(post_id)

    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    if post.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to delete this post.",
        )

    if not await service.delete_post(post_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Post not found"
        )
    
    return True
