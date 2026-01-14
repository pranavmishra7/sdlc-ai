# app/api/auth.py

from datetime import datetime, timedelta
import hashlib
import secrets

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models.user import User
from app.db.models.refresh_token import RefreshToken
from app.core.passwords import verify_password
from app.core.jwt import create_access_token
from app.api.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])

# -------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------

REFRESH_TOKEN_EXPIRE_DAYS = 30


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def _generate_refresh_token() -> str:
    return secrets.token_urlsafe(64)


# -------------------------------------------------------------------
# Login
# -------------------------------------------------------------------

@router.post("/login")
def login(
    email: str,
    password: str,
    db: Session = Depends(get_db),
):
    user = (
        db.query(User)
        .filter(
            User.email == email,
            User.is_active.is_(True),
        )
        .first()
    )

    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    # Access token (short-lived)
    access_token = create_access_token(
        user_id=str(user.id),
        tenant_id=str(user.tenant_id),
        role=user.role,
    )

    # Refresh token (long-lived, hashed in DB)
    raw_refresh_token = _generate_refresh_token()
    refresh_token_hash = _hash_token(raw_refresh_token)

    refresh_token = RefreshToken(
        user_id=user.id,
        tenant_id=user.tenant_id,
        token_hash=refresh_token_hash,
        expires_at=datetime.utcnow()
        + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
    )

    db.add(refresh_token)
    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": raw_refresh_token,
        "token_type": "bearer",
    }


# -------------------------------------------------------------------
# Logout (single-session)
# -------------------------------------------------------------------

@router.post("/logout")
def logout(
    refresh_token: str,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    token_hash = _hash_token(refresh_token)

    db_token = (
        db.query(RefreshToken)
        .filter(
            RefreshToken.token_hash == token_hash,
            RefreshToken.user_id == user["sub"],
            RefreshToken.tenant_id == user["tenant_id"],
            RefreshToken.revoked_at.is_(None),
        )
        .first()
    )

    if not db_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    db_token.revoked_at = datetime.utcnow()
    db.commit()

    return {"message": "Logged out successfully"}

# -------------------------------------------------------------------
# Refresh token (ROTATION)
# -------------------------------------------------------------------

@router.post("/refresh")
def refresh_token(
    refresh_token: str,
    db: Session = Depends(get_db),
):
    token_hash = _hash_token(refresh_token)

    db_token = (
        db.query(RefreshToken)
        .filter(
            RefreshToken.token_hash == token_hash,
            RefreshToken.revoked_at.is_(None),
            RefreshToken.expires_at > datetime.utcnow(),
        )
        .first()
    )

    if not db_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    user = (
        db.query(User)
        .filter(
            User.id == db_token.user_id,
            User.is_active.is_(True),
        )
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User inactive or deleted",
        )

    # 🔁 ROTATE refresh token
    db_token.revoked_at = datetime.utcnow()

    new_raw_refresh = _generate_refresh_token()
    new_refresh_hash = _hash_token(new_raw_refresh)

    new_refresh = RefreshToken(
        user_id=user.id,
        tenant_id=user.tenant_id,
        token_hash=new_refresh_hash,
        expires_at=datetime.utcnow()
        + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
    )

    db.add(new_refresh)

    # 🔐 Issue new access token
    access_token = create_access_token(
        user_id=str(user.id),
        tenant_id=str(user.tenant_id),
        role=user.role,
    )

    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": new_raw_refresh,
        "token_type": "bearer",
    }

@router.post("/logout-all", status_code=status.HTTP_204_NO_CONTENT)
def logout_all_sessions(
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """
    Revoke ALL refresh tokens for the current user.
    This logs the user out from all devices.
    """

    db.query(RefreshToken).filter(
        RefreshToken.user_id == user["sub"],
        RefreshToken.revoked_at.is_(None),
    ).update(
        {"revoked_at": datetime.utcnow()},
        synchronize_session=False,
    )

    db.commit()