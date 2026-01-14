# app/middleware/tenant.py

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from jose import JWTError

from app.core.jwt import decode_token
from app.db.session import SessionLocal


class TenantMiddleware(BaseHTTPMiddleware):
    """
    Extract tenant_id from JWT and set it on the DB session
    so PostgreSQL RLS can enforce isolation.
    """

    async def dispatch(self, request: Request, call_next):
        auth_header = request.headers.get("Authorization")

        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ", 1)[1]

            try:
                payload = decode_token(token)
                tenant_id = payload.get("tenant_id")

                if tenant_id:
                    # Set tenant_id at DB level (RLS)
                    db = SessionLocal()
                    try:
                        db.execute(
                            "SET app.tenant_id = :tenant_id",
                            {"tenant_id": tenant_id},
                        )
                        db.commit()
                    finally:
                        db.close()

            except JWTError:
                # Invalid token → let auth layer handle it later
                pass

        response = await call_next(request)
        return response
