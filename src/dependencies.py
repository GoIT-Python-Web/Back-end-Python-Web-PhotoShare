from fastapi import Depends, HTTPException
from services.auth import get_current_user
from entity.models import User

def get_admin_user(user: User = Depends(get_current_user)):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return user
