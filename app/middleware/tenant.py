# app/middleware/tenant.py

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from jose import JWTError

from app.core.jwt import decode_token
from app.db.session import SessionLocal
from app.db.models.tenant import Tenant, TenantStatus


class TenantMiddleware(BaseHTTPMiddleware):
    """
    Extract tenant_id from JWT, validate tenant status,
    and set it on the DB session so PostgreSQL RLS
    can enforce tenant isolation.
    """

    async def dispatch(self, request: Request, call_next):
        auth_header = request.headers.get("Authorization")

        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ", 1)[1]

            try:
                payload = decode_token(token)
                tenant_id = payload.get("tenant_id")

                if tenant_id:
                    db = SessionLocal()
                    try:
                        # 1. Load tenant
                        tenant = db.get(Tenant, tenant_id)

                        # 2. Enforce tenant status
                        if not tenant or tenant.status != TenantStatus.ACTIVE:
                            raise HTTPException(
                                status_code=status.HTTP_403_FORBIDDEN,
                                detail="Tenant is not active",
                            )

                        # 3. Set tenant context for Postgres RLS
                        db.execute(
                            "SET app.tenant_id = :tenant_id",
                            {"tenant_id": tenant_id},
                        )
                        db.commit()

                    finally:
                        db.close()

            except JWTError:
                # Invalid token → auth layer will handle it
                pass

        response = await call_next(request)
        return response
