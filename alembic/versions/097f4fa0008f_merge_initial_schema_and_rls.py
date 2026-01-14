"""merge_initial_schema_and_rls

Revision ID: 097f4fa0008f
Revises: 504b08949d85, 003_enable_rls_multi_tenancy_v2
Create Date: 2026-01-14 11:19:29.795518

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '097f4fa0008f'
down_revision: Union[str, None] = ('504b08949d85', '003_enable_rls_multi_tenancy_v2')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
