# app/middleware/tenant.py

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy import text

from app.db.session import SessionLocal
from app.db.models.tenant import Tenant, TenantStatus


class TenantMiddleware(BaseHTTPMiddleware):
    """
    Tenant lifecycle + RLS enforcement.

    - Does NOT decode JWT
    - Does NOT resolve user
    - Only enforces tenant if tenant_id is already known
    """

    async def dispatch(self, request: Request, call_next):
        tenant_id = getattr(request.state, "tenant_id", None)

        if tenant_id:
            db = SessionLocal()
            try:
                tenant = db.get(Tenant, tenant_id)

                if not tenant or tenant.status != TenantStatus.ACTIVE:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Tenant is not active",
                    )

                # 🔐 Set tenant context for Postgres RLS
                db.execute(
                    text("SET LOCAL app.tenant_id = :tenant_id"),
                    {"tenant_id": tenant_id},
                )
                db.commit()

            finally:
                db.close()

        return await call_next(request)
