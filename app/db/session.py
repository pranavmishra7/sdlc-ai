# app/db/session.py
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from fastapi import Request
from contextlib import contextmanager

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL environment variable is required")
# create engine with pool_pre_ping to avoid stale connections
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db(request: Request):
    """
    FastAPI dependency that yields a DB session.
    If request.state.user (set by middleware) contains a tenant_id, we
    SET LOCAL app.tenant_id on this DB connection so RLS policies apply.
    """
    db = SessionLocal()
    try:
        # prefer explicit tenant on request.state; otherwise try user payload
        tenant_id = getattr(request.state, "tenant_id", None)
        if not tenant_id:
            user = getattr(request.state, "user", None)
            tenant_id = user.get("tenant_id") if user else None

        if tenant_id:
            db.execute(
                text("SET LOCAL app.tenant_id = :tenant_id"),
                {"tenant_id": tenant_id},
            )

        yield db
    finally:
        db.close()
