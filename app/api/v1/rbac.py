# app/api/v1/rbac.py
from fastapi import Depends, HTTPException, status
from app.api.deps import get_current_user


def require_roles(*roles: str):
    def checker(user=Depends(get_current_user)):
        if user["role"] not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return user
    return checker
