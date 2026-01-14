# app/db/rls.py
from sqlalchemy import text
from sqlalchemy.orm import Session


def set_tenant_context(db: Session, tenant_id: str) -> None:
    """
    Sets PostgreSQL RLS tenant context.
    Scoped to the current transaction / connection.

    Must be called AFTER a DB session is created.
    """
    # Uses SET LOCAL so the setting is transaction-scoped
    db.execute(
        text("SET LOCAL app.tenant_id = :tenant_id"),
        {"tenant_id": tenant_id},
    )
