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
from src.services.cloudinary_qr_service import UploadFileService, QrService
from src.services.post_service import PostService
from typing import List
from src.entity.models import User
from src.core.dependencies import role_required

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
    db: AsyncSession = Depends(get_db)
):
    service = PostService(PostRepository(db))
    
    return await service.get_post_by_id(post_id)

@router.get("/user/{user_id}", response_model=List[PostResponse])
async def get_posts_by_user(
    db: AsyncSession = Depends(get_db), 
    current_user: User = role_required("user", "admin"),
    user_id: UUID = None
):
    service = PostService(PostRepository(db, current_user, user_id))
    
    return await service.get_all_user_posts()

@router.put("/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: UUID, update_data: PostUpdateRequest = Body(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = role_required("user"),
):
    service = PostService(PostRepository(db, current_user))
    post = await service.get_post_by_id(post_id)

    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    
    author_or_admin = await service.is_author_or_admin(post)

    if not author_or_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to update this post.",
        )
    
    if not await service.update_post(post_id, update_data.description):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return await service.update_post(post_id, update_data.description)

@router.post("/", response_model=PostCreateResponse)
async def create_post(
    post_data: PostCreateModel = Body(...),
    db: AsyncSession = Depends((get_db)),
    current_user: User = role_required("user", "admin")): 

    service = PostService(PostRepository(db, current_user))
    return await service.create_post(post_data)

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

    author_or_admin = await service.is_author_or_admin(post)

    if not author_or_admin:
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

@router.post("/upload-filtered-image/")
async def upload_filtered_image(
    file: UploadFile = File(...),
    width: int = Form(...),
    height: int = Form(...),
    crop: str = Form(...),
    effect: str = Form(...),
    current_user: User = role_required("user", "admin")
):
    image_url = await UploadFileService.upload_with_filters(
        file=file,
        width=width,
        height=height,
        crop=crop,
        effect=effect
    )
    return {"image_url": image_url}

@router.post("/generate-qr")
async def generate_qr_code_from_url(
    url: str = Body(..., embed=True),
    current_user: User = role_required("user", "admin")
):
    try:
        qr_code_image = QrService.generate_qr_code(url)
        return {"qr_code": qr_code_image}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"QR generation failed: {str(e)}")
