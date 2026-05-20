"""create specialties

Revision ID: 0003
Revises: 0002
Create Date: 2026-05-20
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


_SEED = [
    "Clínico Geral",
    "Cardiologia",
    "Dermatologia",
    "Pediatria",
    "Ortopedia",
]


def upgrade() -> None:
    op.create_table(
        "specialties",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.UniqueConstraint("name", name="uq_specialties_name"),
    )

    specialties = sa.table(
        "specialties",
        sa.column("name", sa.String),
        sa.column("description", sa.Text),
        sa.column("is_active", sa.Boolean),
    )
    op.bulk_insert(
        specialties,
        [{"name": n, "description": None, "is_active": True} for n in _SEED],
    )


def downgrade() -> None:
    op.drop_table("specialties")
