import uuid
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.jwt import create_access_token
from app.db.session import SessionLocal
from app.db.models.project import Project
from app.db.models.tenant import Tenant

client = TestClient(app)


def _auth_header(tenant_id: str, role: str = "admin"):
    token = create_access_token(
        user_id=str(uuid.uuid4()),
        tenant_id=tenant_id,
        role=role,
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def tenants():
    """
    Create two tenants directly in DB (bypassing API).
    """
    db = SessionLocal()
    try:
        tenant_a = Tenant(id=uuid.uuid4(), name="Tenant A")
        tenant_b = Tenant(id=uuid.uuid4(), name="Tenant B")

        db.add_all([tenant_a, tenant_b])
        db.commit()

        yield str(tenant_a.id), str(tenant_b.id)
    finally:
        db.close()


def test_rls_isolation_projects(tenants):
    tenant_a_id, tenant_b_id = tenants

    # ------------------------------
    # Tenant A creates a project
    # ------------------------------
    response = client.post(
        "/api/v1/projects/",
        json={"name": "Project A1"},
        headers=_auth_header(tenant_a_id),
    )
    assert response.status_code in (200, 201)

    # ------------------------------
    # Tenant A lists projects
    # ------------------------------
    response = client.get(
        "/api/v1/projects/",
        headers=_auth_header(tenant_a_id),
    )
    assert response.status_code == 200
    data = response.json()

    assert len(data) == 1
    assert data[0]["name"] == "Project A1"

    # ------------------------------
    # Tenant B lists projects
    # ------------------------------
    response = client.get(
        "/api/v1/projects/",
        headers=_auth_header(tenant_b_id),
    )
    assert response.status_code == 200
    data = response.json()

    # 🚨 CRITICAL ASSERTION
    # If RLS is broken, this will return Tenant A's project
    assert data == []

def test_rls_blocks_cross_tenant_direct_db_access(tenants):
    tenant_a_id, tenant_b_id = tenants

    db = SessionLocal()
    try:
        # Pretend we're tenant A
        db.execute(
            "SET LOCAL app.tenant_id = :tid",
            {"tid": tenant_a_id},
        )

        db.add(Project(id=uuid.uuid4(), tenant_id=tenant_a_id, name="DB Project"))
        db.commit()
    finally:
        db.close()

    # Now access as tenant B via API
    response = client.get(
        "/api/v1/projects/",
        headers=_auth_header(tenant_b_id),
    )

    assert response.status_code == 200
    assert response.json() == []
