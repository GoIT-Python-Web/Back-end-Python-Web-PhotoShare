from fastapi import APIRouter, Depends
from src.schemas.users import MyselfOut
from src.entity.models import User
from src.core.security import get_current_user


router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=MyselfOut)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
):
    return current_user