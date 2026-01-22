# app/api/v1/projects.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.db.models.project import Project
from app.api.v1.rbac import require_roles

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("/")
def list_projects(
    db: Session = Depends(get_db),
    user=Depends(require_roles("ADMIN", "USER", "OWNER")),
):
    # RLS will filter to tenant rows automatically.
    return db.query(Project).all()
