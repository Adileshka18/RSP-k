"""add enterprise favorites

Revision ID: 20260418_4a7d9f1c2b0e
Revises: 20260418_2b2a8d74f1b1
Create Date: 2026-04-18 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "20260418_4a7d9f1c2b0e"
down_revision = "20260418_2b2a8d74f1b1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "enterprise_favorites",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("user_id", sa.BigInteger(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("enterprise_id", sa.BigInteger(), sa.ForeignKey("enterprises.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index(
        "uq_enterprise_favorite",
        "enterprise_favorites",
        ["user_id", "enterprise_id"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("uq_enterprise_favorite", table_name="enterprise_favorites")
    op.drop_table("enterprise_favorites")
