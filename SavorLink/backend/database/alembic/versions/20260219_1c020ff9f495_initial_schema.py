"""initial schema

Revision ID: 1c020ff9f495
Revises:
Create Date: 2026-02-19 17:29:46.736251

"""

from typing import Sequence, Union

from alembic import op

from backend.database.models import Base

# revision identifiers, used by Alembic.
revision: str = "1c020ff9f495"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _create_enum_types() -> None:
    op.execute("CREATE TYPE user_role AS ENUM ('ADMIN', 'BUYER', 'SUPPLIER')")
    op.execute(
        "CREATE TYPE order_status AS ENUM ('CREATED', 'CONFIRMED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED')"
    )
    op.execute("CREATE TYPE payment_status AS ENUM ('PENDING', 'PAID', 'FAILED', 'REFUNDED')")
    op.execute("CREATE TYPE document_type AS ENUM ('INVOICE', 'CONTRACT', 'ACT')")


def _drop_enum_types() -> None:
    op.execute("DROP TYPE IF EXISTS document_type")
    op.execute("DROP TYPE IF EXISTS payment_status")
    op.execute("DROP TYPE IF EXISTS order_status")
    op.execute("DROP TYPE IF EXISTS user_role")


def upgrade() -> None:
    """Create the full application schema."""
    _create_enum_types()
    Base.metadata.create_all(bind=op.get_bind())


def downgrade() -> None:
    """Drop the full application schema."""
    Base.metadata.drop_all(bind=op.get_bind())
    _drop_enum_types()
