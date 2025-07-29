"""unique provider id

Revision ID: b1e93f973592
Revises: 6f3503db5b05
Create Date: 2025-07-29 09:10:10.984022

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b1e93f973592"
down_revision: Union[str, Sequence[str], None] = "6f3503db5b05"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_unique_constraint(None, "identities", ["provider_id"])


def downgrade() -> None:
    op.drop_constraint(None, "identities", type_="unique")
