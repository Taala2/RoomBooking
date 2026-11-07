"""delete bookings together with their room

Revision ID: 0004
Revises: 0003
Create Date: 2026-11-07

The service refuses to delete a room with upcoming active bookings,
so the cascade only removes past and canceled bookings.
"""
from typing import Sequence, Union

from alembic import op


revision: str = "0004"
down_revision: Union[str, Sequence[str], None] = "0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

FK_NAME = "bookings_room_id_fkey"


def upgrade() -> None:
    op.drop_constraint(FK_NAME, "bookings", type_="foreignkey")
    op.create_foreign_key(FK_NAME, "bookings", "rooms", ["room_id"], ["id"], ondelete="CASCADE")


def downgrade() -> None:
    op.drop_constraint(FK_NAME, "bookings", type_="foreignkey")
    op.create_foreign_key(FK_NAME, "bookings", "rooms", ["room_id"], ["id"])
