"""add city to enterprises

Revision ID: 20260419_0d7e8d5c9b1a
Revises: 20260418_4a7d9f1c2b0e
Create Date: 2026-04-19 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "20260419_0d7e8d5c9b1a"
down_revision = "20260418_4a7d9f1c2b0e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE enterprises ADD COLUMN IF NOT EXISTS city TEXT")


def downgrade() -> None:
    op.drop_column("enterprises", "city")
