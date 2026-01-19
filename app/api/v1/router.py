# app/api/v1/router.py

print("ROUTER: start import")

from fastapi import APIRouter
print("ROUTER: fastapi imported")

from app.api.v1.workflows import router as workflows_router
print("ROUTER: workflows router imported")

from app.api.v1.health import router as health_router
print("ROUTER: health router imported")

from app.api.v1 import projects
print("ROUTER: projects router imported")

from app.api import auth
print("ROUTER: auth router imported")

api_router = APIRouter()
print("ROUTER: api_router created")

# -----------------------------
# Route registration
# -----------------------------

print("ROUTER: including auth router")
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])

print("ROUTER: including projects router (v1)")
api_router.include_router(projects.router, prefix="/api/v1/projects", tags=["projects"])

print("ROUTER: including health router")
api_router.include_router(health_router, prefix="/api/health", tags=["health"])

print("ROUTER: including workflows router")
api_router.include_router(workflows_router, prefix="/api/workflows", tags=["workflows"])

print("ROUTER: end import")
