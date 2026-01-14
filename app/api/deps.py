# app/api/deps.py
from fastapi import Request, HTTPException, status


def get_current_user(request: Request):
    """
    Returns the authenticated user payload put on request.state by middleware.
    If no user is present, raise 401.
    """
    user = getattr(request.state, "user", None)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    return user
