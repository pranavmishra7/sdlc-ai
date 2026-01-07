from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from app.api.v1 import workflows, health

BASE_DIR = Path(__file__).resolve().parent  # app/

app = FastAPI(title="SDLC AI")

# API
app.include_router(health.router, prefix="/v1")
app.include_router(workflows.router, prefix="/v1")

# Redirect /ui -> /ui/
@app.get("/ui", include_in_schema=False)
def ui_redirect():
    return RedirectResponse(url="/ui/")

# Static UI
app.mount(
    "/ui",
    StaticFiles(directory=str(BASE_DIR / "ui"), html=True),
    name="ui",
)
