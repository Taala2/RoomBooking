"""align schema with models: timestamptz, unique login/email, role enum

Revision ID: 0002
Revises: 0001
Create Date: 2026-11-07

Existing timestamps were written into "timestamp without time zone" columns,
so PostgreSQL stored them in the server TimeZone. They are converted using
that same TimeZone, so the moments in time stay the same.
"""
from typing import Sequence, Union

from alembic import op


revision: str = "0002"
down_revision: Union[str, Sequence[str], None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

BOOKING_TIME_COLUMNS = ("start_time", "end_time", "created_at")


def upgrade() -> None:
    for column in BOOKING_TIME_COLUMNS:
        op.execute(
            f"ALTER TABLE bookings ALTER COLUMN {column} TYPE TIMESTAMP WITH TIME ZONE "
            f"USING {column} AT TIME ZONE current_setting('TimeZone')"
        )

    op.create_index("ix_bookings_user_id", "bookings", ["user_id"])

    op.alter_column("users", "email", nullable=False)
    op.execute("ALTER TABLE users ALTER COLUMN role TYPE userrole USING role::userrole")
    op.create_unique_constraint("users_login_key", "users", ["login"])
    op.create_unique_constraint("users_email_key", "users", ["email"])


def downgrade() -> None:
    op.drop_constraint("users_email_key", "users", type_="unique")
    op.drop_constraint("users_login_key", "users", type_="unique")
    op.execute("ALTER TABLE users ALTER COLUMN role TYPE VARCHAR(50) USING role::text")
    op.alter_column("users", "email", nullable=True)

    op.drop_index("ix_bookings_user_id", table_name="bookings")

    for column in BOOKING_TIME_COLUMNS:
        op.execute(
            f"ALTER TABLE bookings ALTER COLUMN {column} TYPE TIMESTAMP WITHOUT TIME ZONE "
            f"USING {column} AT TIME ZONE current_setting('TimeZone')"
        )
