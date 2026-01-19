"""add user status and lifecycle fields

Revision ID: 9d5faee0da34
Revises: 527f7d53aed3
Create Date: 2026-01-19 12:28:41.403377

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9d5faee0da34'
down_revision: Union[str, None] = '527f7d53aed3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # 1. Create enum type explicitly
    user_status_enum = sa.Enum(
        "INVITED",
        "ACTIVE",
        "DISABLED",
        "DELETED",
        name="user_status_enum",
    )
    user_status_enum.create(op.get_bind(), checkfirst=True)

    # 2. Add columns
    op.add_column(
        "users",
        sa.Column(
            "status",
            user_status_enum,
            server_default="INVITED",
            nullable=False,
        ),
    )

    op.add_column(
        "users",
        sa.Column(
            "invited_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )

    op.add_column(
        "users",
        sa.Column(
            "last_login_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )

def downgrade() -> None:
    op.drop_column("users", "last_login_at")
    op.drop_column("users", "invited_at")
    op.drop_column("users", "status")

    user_status_enum = sa.Enum(
        "INVITED",
        "ACTIVE",
        "DISABLED",
        "DELETED",
        name="user_status_enum",
    )
    user_status_enum.drop(op.get_bind(), checkfirst=True)

