from fastapi import Depends, HTTPException
from src.core.security import get_current_user
from typing import List

def require_role(required_roles: List[str]):
    def decorator(user: dict = Depends(get_current_user)):
        if not any(role in user["roles"] for role in required_roles):
            raise HTTPException(status_code=403, detail="Access denied")
        return user
    return decorator

def admin_required(user: dict = Depends(require_role(["admin"]))):
    return user

def user_required(user: dict = Depends(require_role(["user", "admin"]))):
    return user


