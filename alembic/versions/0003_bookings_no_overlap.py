"""forbid overlapping active bookings of the same room

Revision ID: 0003
Revises: 0002
Create Date: 2026-11-07

The database guarantees what the service check cannot guarantee under
concurrent requests. '[)' makes back-to-back bookings (10-11 and 11-12) valid.
Status is compared with 'ACTIVE' because SQLAlchemy stores enum member names.
"""
from typing import Sequence, Union

from alembic import op


revision: str = "0003"
down_revision: Union[str, Sequence[str], None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS btree_gist")
    op.execute(
        "ALTER TABLE bookings ADD CONSTRAINT bookings_no_overlap "
        "EXCLUDE USING gist (room_id WITH =, tstzrange(start_time, end_time, '[)') WITH &&) "
        "WHERE (status = 'ACTIVE')"
    )


def downgrade() -> None:
    # btree_gist is left installed: other objects may depend on it.
    op.execute("ALTER TABLE bookings DROP CONSTRAINT bookings_no_overlap")
