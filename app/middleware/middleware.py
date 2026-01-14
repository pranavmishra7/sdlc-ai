# app/api/middleware.py
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.api.deps import get_current_user

class UserContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            request.state.user = await get_current_user(request)
        except Exception:
            request.state.user = None
        return await call_next(request)
