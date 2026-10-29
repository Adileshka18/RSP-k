"""add user token version

Revision ID: 20260418_2b2a8d74f1b1
Revises: 89b18b3ad956
Create Date: 2026-04-18 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "20260418_2b2a8d74f1b1"
down_revision = "89b18b3ad956"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS token_version INTEGER DEFAULT 0 NOT NULL")


def downgrade() -> None:
    op.drop_column("users", "token_version")
