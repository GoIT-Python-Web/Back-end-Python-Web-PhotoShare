from fastapi import APIRouter, Depends, HTTPException, status, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas.post import PostResponse, PostDeleteResponse, PostUpdateResponse
from uuid import UUID
from src.database.db import get_db
from src.repositories.post_repository import PostRepository
from src.services.cloudinary_qr_service import UploadFileService
from src.services.post_service import PostService
from typing import List, Optional

router = APIRouter(prefix='/posts', tags=['posts'])

@router.get("/{post_id}", response_model=PostResponse)
async def get_post(post_id: UUID, db: AsyncSession = Depends(get_db)):
    service = PostService(PostRepository(db))
    
    return await service.get_post_by_id(post_id)

@router.get("/", response_model=List[PostResponse])
async def get_posts(db: AsyncSession = Depends(get_db)):
    service = PostService(PostRepository(db))
    
    return await service.get_all_posts()

@router.put("/{post_id}", response_model=bool)
async def update_post(post_id: UUID, description: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    service = PostService(PostRepository(db))
    if not await service.update_post(post_id, description):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return True

@router.post("/", response_model=PostResponse)
async def create_post(
    title: str, 
    image: UploadFile,
    description: Optional[str], 
    db: AsyncSession = Depends(get_db)
):
    service = PostService(PostRepository(db))

    try:
        image_url = await UploadFileService.upload_file(image)
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    
    return await service.create_post(title, image_url, description)

@router.delete("/{post_id}", response_model=bool)
async def delete_post(post_id: UUID, db: AsyncSession = Depends(get_db)):
    service = PostService(PostRepository(db))
    if not await service.delete_post(post_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return True
