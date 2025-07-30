"""migrate updates to users table

Revision ID: bd2c2ed302d8
Revises: f7065eeef3bf
Create Date: 2025-07-22 13:23:02.562889

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "bd2c2ed302d8"
down_revision: Union[str, Sequence[str], None] = "f7065eeef3bf"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users", sa.Column("auth_provider", sa.String(length=50), nullable=False)
    )
    op.add_column("users", sa.Column("oauth_sub", sa.String(length=255), nullable=True))
    op.alter_column(
        "users", "username", existing_type=sa.VARCHAR(length=50), nullable=True
    )
    op.alter_column("users", "password", existing_type=sa.VARCHAR(), nullable=True)
    op.create_index(op.f("ix_users_oauth_sub"), "users", ["oauth_sub"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_users_oauth_sub"), table_name="users")
    op.alter_column("users", "password", existing_type=sa.VARCHAR(), nullable=False)
    op.alter_column(
        "users", "username", existing_type=sa.VARCHAR(length=50), nullable=False
    )
    op.drop_column("users", "oauth_sub")
    op.drop_column("users", "auth_provider")
