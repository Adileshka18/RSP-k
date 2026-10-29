"""add user names and enterprise desc

Revision ID: 20260420_111111111111
Revises: 20260419_0d7e8d5c9b1a
Create Date: 2026-04-20 20:30:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "20260420_111111111111"
down_revision = "20260419_0d7e8d5c9b1a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS first_name TEXT")
    op.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS last_name TEXT")
    op.execute("ALTER TABLE enterprises ADD COLUMN IF NOT EXISTS description TEXT")


def downgrade() -> None:
    op.drop_column("enterprises", "description")
    op.drop_column("users", "last_name")
    op.drop_column("users", "first_name")
