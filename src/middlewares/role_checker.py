from fastapi import Depends, HTTPException
from services.auth import get_current_user
from entity.models import User

def role_required(role: str):
    def wrapper(user: User = Depends(get_current_user)):
        if user.role != role:
            raise HTTPException(status_code=403, detail="Not enough permissions")
        return user
    return wrapper
