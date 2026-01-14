from fastapi import Request
from app.db.session import SessionLocal
from sqlalchemy.orm import Session
from fastapi import Depends
from app.db.session import SessionLocal
from app.db.rls import set_tenant_id
from app.auth.deps import get_current_tenant_id

def get_db(
    tenant_id: str = Depends(get_current_tenant_id),
):
    db: Session = SessionLocal()
    try:
        set_tenant_id(db.connection().connection, tenant_id)
        yield db
    finally:
        db.close()
