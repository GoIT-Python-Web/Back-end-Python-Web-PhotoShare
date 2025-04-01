from fastapi import Depends, HTTPException
from src.core.security import get_current_user

def admin_required(user: dict = Depends(get_current_user)):
    if not user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin access required")
    return user
