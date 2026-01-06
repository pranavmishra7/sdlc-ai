from fastapi import FastAPI
from app.api.v1 import workflows, health
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="SDLC AI")

app.include_router(health.router, prefix="/v1")
app.include_router(workflows.router, prefix="/v1")

app.mount("/", StaticFiles(directory="app/ui", html=True), name="ui")
