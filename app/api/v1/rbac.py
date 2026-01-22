from fastapi import Depends, HTTPException, status
from typing import Iterable
from app.api.deps import get_current_user
from app.db.models.user import User


def require_roles(*roles: Iterable[str]):
    """
    RBAC dependency.
    Usage:
        Depends(require_roles("ADMIN", "OWNER"))
    """

    def checker(user: User = Depends(get_current_user)):
        if user.role not in roles:
            print(f"User role {user.role} not in required roles {roles}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return user

    return checker
