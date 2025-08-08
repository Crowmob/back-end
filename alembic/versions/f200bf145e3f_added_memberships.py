"""added memberships

Revision ID: f200bf145e3f
Revises: 27619efea0a4
Create Date: 2025-08-08 15:27:29.591160

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "f200bf145e3f"
down_revision: Union[str, Sequence[str], None] = "27619efea0a4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "membership_requests",
        sa.Column("type", sa.String(length=50), nullable=False),
        sa.Column("from_id", sa.Integer(), nullable=False),
        sa.Column("to_id", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_membership_requests_id"), "membership_requests", ["id"], unique=False
    )
    op.create_table(
        "memberships",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("company_id", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_memberships_id"), "memberships", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_memberships_id"), table_name="memberships")
    op.drop_table("memberships")
    op.drop_index(op.f("ix_membership_requests_id"), table_name="membership_requests")
    op.drop_table("membership_requests")
