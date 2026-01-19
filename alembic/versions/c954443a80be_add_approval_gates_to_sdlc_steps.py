"""add approval gates to sdlc steps

Revision ID: c954443a80be
Revises: 6f201ae488c2
Create Date: 2026-01-19 13:57:22.410918
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c954443a80be"
down_revision: Union[str, None] = "6f201ae488c2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1️⃣ Add requires_approval flag
    op.add_column(
        "sdlc_job_steps",
        sa.Column(
            "requires_approval",
            sa.Boolean(),
            server_default="false",
            nullable=False,
        ),
    )

    # 2️⃣ Create approval_status_enum explicitly
    approval_status_enum = sa.Enum(
        "PENDING",
        "APPROVED",
        "REJECTED",
        name="approval_status_enum",
    )
    approval_status_enum.create(op.get_bind(), checkfirst=True)

    # 3️⃣ Add approval_status column using enum
    op.add_column(
        "sdlc_job_steps",
        sa.Column(
            "approval_status",
            approval_status_enum,
            nullable=True,
        ),
    )

    # 4️⃣ Add approver + timestamp
    op.add_column(
        "sdlc_job_steps",
        sa.Column(
            "approved_by",
            sa.UUID(),
            nullable=True,
        ),
    )

    op.add_column(
        "sdlc_job_steps",
        sa.Column(
            "approved_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )

    # 5️⃣ Foreign key to users
    op.create_foreign_key(
        op.f("fk_sdlc_job_steps_approved_by_users"),
        "sdlc_job_steps",
        "users",
        ["approved_by"],
        ["id"],
    )


def downgrade() -> None:
    # 1️⃣ Drop FK first
    op.drop_constraint(
        op.f("fk_sdlc_job_steps_approved_by_users"),
        "sdlc_job_steps",
        type_="foreignkey",
    )

    # 2️⃣ Drop columns
    op.drop_column("sdlc_job_steps", "approved_at")
    op.drop_column("sdlc_job_steps", "approved_by")
    op.drop_column("sdlc_job_steps", "approval_status")
    op.drop_column("sdlc_job_steps", "requires_approval")

    # 3️⃣ Drop enum LAST
    approval_status_enum = sa.Enum(
        "PENDING",
        "APPROVED",
        "REJECTED",
        name="approval_status_enum",
    )
    approval_status_enum.drop(op.get_bind(), checkfirst=True)
