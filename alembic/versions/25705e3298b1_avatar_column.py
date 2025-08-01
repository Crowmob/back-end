"""avatar column

Revision ID: 25705e3298b1
Revises: 3d5d90ae3651
Create Date: 2025-07-31 09:49:40.325993

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "25705e3298b1"
down_revision: Union[str, Sequence[str], None] = "3d5d90ae3651"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "users",
        "avatar",
        existing_type=sa.VARCHAR(),
        type_=sa.LargeBinary(),
        existing_nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        "users",
        "avatar",
        existing_type=sa.LargeBinary(),
        type_=sa.VARCHAR(),
        existing_nullable=True,
    )
