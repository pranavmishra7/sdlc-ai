from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import hashlib
import secrets

from app.db.models.user import User
from app.db.models.refresh_token import RefreshToken
from app.core.passwords import verify_password
from app.core.jwt import create_access_token
from app.api.deps import get_db

router = APIRouter(prefix="/auth", tags=["auth"])

REFRESH_TOKEN_EXPIRE_DAYS = 30


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def _generate_refresh_token() -> str:
    return secrets.token_urlsafe(64)


@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    OAuth2-compatible login.
    Swagger sends:
      - username
      - password
    """

    user = (
        db.query(User)
        .filter(
            User.email == form_data.username,
            User.is_active.is_(True),
        )
        .first()
    )

    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    access_token = create_access_token(
        user_id=str(user.id),
        tenant_id=str(user.tenant_id),
        role=user.role,
    )

    raw_refresh_token = _generate_refresh_token()
    refresh_token_hash = _hash_token(raw_refresh_token)

    refresh_token = RefreshToken(
        user_id=user.id,
        tenant_id=user.tenant_id,
        token_hash=refresh_token_hash,
        expires_at=datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
    )

    db.add(refresh_token)
    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": raw_refresh_token,
        "token_type": "bearer",
    }
