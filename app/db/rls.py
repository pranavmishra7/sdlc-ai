# app/db/rls.py
from sqlalchemy.orm import Session
from sqlalchemy import text
from uuid import UUID

def set_tenant_context(db: Session, tenant_id: str | UUID):
    """
    Set tenant_id for PostgreSQL RLS.

    IMPORTANT:
    - SET LOCAL does NOT support bind parameters
    - Value MUST be inlined as a string
    - UUID is cast implicitly by Postgres
    """

    if isinstance(tenant_id, UUID):
        tenant_id = str(tenant_id)

    # SAFE because:
    # - tenant_id comes from JWT / DB, not user input
    # - UUID format is strictly controlled
    sql = f"SET LOCAL app.tenant_id = '{tenant_id}'"

    db.execute(text(sql))
