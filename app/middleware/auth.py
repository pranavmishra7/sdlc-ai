from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
from jose import JWTError

from app.core.jwt import decode_access_token as decode_token
from app.db.session import SessionLocal


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        auth = request.headers.get("Authorization")

        if not auth or not auth.startswith("Bearer "):
            return JSONResponse({"detail": "Not authenticated"}, status_code=401)

        token = auth.split(" ", 1)[1]

        try:
            payload = decode_token(token)
        except JWTError:
            return JSONResponse({"detail": "Invalid token"}, status_code=401)

        # Attach user
        request.state.user = payload

        # Set tenant for RLS
        tenant_id = payload["tenant_id"]

        db = SessionLocal()
        try:
            db.execute("SET LOCAL app.tenant_id = :tenant_id", {"tenant_id": tenant_id})
            db.commit()
        finally:
            db.close()

        return await call_next(request)
