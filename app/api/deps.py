# app/api/deps.py

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError

from app.core.jwt import decode_token
from app.db.session import SessionLocal
from app.db.models.user import User, UserStatus


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db=Depends(get_db),
) -> User:
    """
    Resolve the authenticated user from JWT
    and enforce SaaS user lifecycle rules.
    """

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_token(token)
        user_id = payload.get("sub")
        tenant_id = payload.get("tenant_id")

        if not user_id or not tenant_id:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    # Load user (RLS already enforces tenant isolation)
    user = db.get(User, user_id)

    if not user:
        raise credentials_exception

    # 🔒 USER STATUS ENFORCEMENT (CRITICAL)
    if user.status != UserStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is not active",
        )

    return user
