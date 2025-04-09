from fastapi import (
    APIRouter, Body, Depends, File, Form, HTTPException, status, UploadFile 
)
from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas.post import (
    PostResponse, PostCreateModel, PostCreateResponse, PostUpdateRequest
)
from uuid import UUID
from src.database.db import get_db
from src.repositories.post_repository import PostRepository
from src.services.post_service import PostService
from typing import List
from src.entity.models import User
from src.core.dependencies import role_required

import json

router = APIRouter(prefix='/posts', tags=['posts'])

@router.get("/", response_model=List[PostResponse])
async def get_posts(
    db: AsyncSession = Depends(get_db), 
):
    service = PostService(PostRepository(db))
    
    return await service.get_all_posts()

@router.get("/{post_id}", response_model=PostResponse)
async def get_post(
    post_id: UUID, 
    db: AsyncSession = Depends(get_db), 
    current_user: User = role_required("user", "admin")
):
    service = PostService(PostRepository(db, current_user))
    
    return await service.get_post_by_id(post_id)

@router.put("/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: UUID, update_data: PostUpdateRequest = Body(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = role_required("user", "admin"),
):
    service = PostService(PostRepository(db, current_user))
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

@router.post("/", response_model=PostCreateResponse)
async def create_post(
    title: str = Form(...),
    description: str = Form(None),
    location: str = Form(None),
    tags: str = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends((get_db)),
    current_user: User = role_required("user", "admin")): 

    post_data = PostCreateModel(
        title=title,
        description=description,
        image_url='',
        location=location,
        tags=json.loads(tags)
    )

    service = PostService(PostRepository(db, current_user))
    return await service.create_post(post_data, file)

@router.delete("/{post_id}", response_model=bool)
async def delete_post(
    post_id: UUID, 
    db: AsyncSession = Depends(get_db),
    current_user: User = role_required("user", "admin"),
):
    service = PostService(PostRepository(db, current_user))
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
