from fastapi import FastAPI

from app.middleware.tenant import TenantMiddleware
from app.middleware.middleware import UserContextMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from app.api.v1.router import api_router
from fastapi_limiter import FastAPILimiter
from redis.asyncio import Redis
from app.middleware.tenant_context import TenantContextMiddleware
from app.api.v1 import projects

app = FastAPI(
    title="SDLC AI Platform",
    version="1.0.0",
)

@app.on_event("startup")
async def startup():
    redis = Redis.from_url(
        "redis://localhost:6379",
        encoding="utf-8",
        decode_responses=True,
    )
    await FastAPILimiter.init(redis)

app.add_middleware(TenantContextMiddleware)    
app.add_middleware(TenantMiddleware)
app.add_middleware(UserContextMiddleware)


# -------------------------------------------------
# API Routers
# -------------------------------------------------


app.include_router(
    api_router,
    prefix="/api/v1"
)

# -------------------------------------------------
# Admin UI (Static)
# -------------------------------------------------

# Serve static UI files
app.mount(
    "/ui",
    StaticFiles(directory="app/ui", html=True),
    name="ui",
)


# Friendly admin entrypoint
@app.get("/admin", include_in_schema=False)
def admin_ui():
    """
    Redirect to Admin Console UI.
    """
    return RedirectResponse(url="/ui/admin.html")
