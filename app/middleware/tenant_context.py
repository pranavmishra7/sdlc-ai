from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from app.db.session import SessionLocal
from app.db.rls import set_tenant_context
from app.api.deps import get_current_user

class TenantContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Skip auth routes
        if request.url.path.startswith("/auth"):
            return await call_next(request)

        # Resolve user
        user = await get_current_user(request)
        tenant_id = user["tenant_id"]

        # Attach DB session
        db = SessionLocal()
        try:
            set_tenant_context(db, tenant_id)
            request.state.db = db
            response = await call_next(request)
            db.commit()
            return response
        finally:
            db.close()
