from fastapi import Depends, HTTPException, status
from src.entity.models import User
from src.core.security import get_current_user
#from src.routes.auth import get_current_user

def role_required(*allowed_roles: str):
    async def verify_role(current_user: User = Depends(get_current_user)):
        if not current_user.type == 'admin':
            if not current_user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You are in ban list"
                )
            if current_user.type not in allowed_roles or not current_user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You do not have permission to access this resource",
                )
        return current_user
    return Depends(verify_role)