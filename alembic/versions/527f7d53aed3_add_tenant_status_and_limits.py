"""add tenant status and limits

Revision ID: 527f7d53aed3
Revises: 097f4fa0008f
Create Date: 2026-01-19 12:20:21.125582

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '527f7d53aed3'
down_revision: Union[str, None] = '097f4fa0008f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create enum type explicitly
    tenant_status_enum = sa.Enum(
        "CREATED",
        "ACTIVE",
        "SUSPENDED",
        "DELETED",
        name="tenant_status_enum",
    )
    tenant_status_enum.create(op.get_bind(), checkfirst=True)

    # 2. Add columns
    op.add_column(
        "tenants",
        sa.Column(
            "status",
            tenant_status_enum,
            server_default="CREATED",
            nullable=False,
        ),
    )

    op.add_column(
        "tenants",
        sa.Column(
            "plan",
            sa.String(),
            server_default="free",
            nullable=False,
        ),
    )

    op.add_column(
        "tenants",
        sa.Column(
            "max_projects",
            sa.Integer(),
            server_default="3",
            nullable=False,
        ),
    )

    op.add_column(
        "tenants",
        sa.Column(
            "max_users",
            sa.Integer(),
            server_default="5",
            nullable=False,
        ),
    )

    op.add_column(
        "tenants",
        sa.Column(
            "llm_monthly_tokens",
            sa.Integer(),
            server_default="100000",
            nullable=False,
        ),
    )

def downgrade() -> None:
    op.drop_column("tenants", "llm_monthly_tokens")
    op.drop_column("tenants", "max_users")
    op.drop_column("tenants", "max_projects")
    op.drop_column("tenants", "plan")
    op.drop_column("tenants", "status")

    tenant_status_enum = sa.Enum(
        "CREATED",
        "ACTIVE",
        "SUSPENDED",
        "DELETED",
        name="tenant_status_enum",
    )
    tenant_status_enum.drop(op.get_bind(), checkfirst=True)
