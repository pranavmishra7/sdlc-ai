# app/api/v1/router.py
from fastapi import APIRouter
from app.api.v1.workflows import router as workflows_router
from app.api.v1.health import router as health_router
from app.api.v1 import projects
from app.api import auth

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(projects.router)
api_router.include_router(health_router, prefix="/api")
api_router.include_router(workflows_router, prefix="/api")
api_router.include_router(api_router, prefix="/api")
api_router.include_router(projects.router, prefix="/api/v1")