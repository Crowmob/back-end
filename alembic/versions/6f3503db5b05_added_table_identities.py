"""added table identities

Revision ID: 6f3503db5b05
Revises: 5c16531080e1
Create Date: 2025-07-28 12:06:13.911618

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "6f3503db5b05"
down_revision: Union[str, Sequence[str], None] = "5c16531080e1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "identities",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("provider", sa.String(length=50), nullable=False),
        sa.Column("provider_id", sa.String(length=255), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_identities_id"), "identities", ["id"], unique=False)
    op.drop_index(op.f("ix_users_oauth_id"), table_name="users")
    op.drop_column("users", "auth_provider")
    op.drop_column("users", "oauth_id")


def downgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "oauth_id", sa.VARCHAR(length=255), autoincrement=False, nullable=True
        ),
    )
    op.add_column(
        "users",
        sa.Column(
            "auth_provider", sa.VARCHAR(length=50), autoincrement=False, nullable=False
        ),
    )
    op.create_index(op.f("ix_users_oauth_id"), "users", ["oauth_id"], unique=True)
    op.drop_index(op.f("ix_identities_id"), table_name="identities")
    op.drop_table("identities")
