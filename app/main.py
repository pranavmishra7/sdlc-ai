from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

from app.api.v1.workflows import router as workflows_router
from app.api.v1.health import router as health_router


app = FastAPI(
    title="SDLC AI Platform",
    version="1.0.0",
)


# -------------------------------------------------
# API Routers
# -------------------------------------------------

app.include_router(health_router, prefix="/api")
app.include_router(workflows_router, prefix="/api")


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
