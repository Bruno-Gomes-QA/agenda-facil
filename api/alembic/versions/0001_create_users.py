"""create users and patients tables

Revision ID: 0001
Revises:
Create Date: 2026-05-19

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    user_role_enum = sa.Enum("paciente", "recepcionista", "medico", name="user_role")

    # ── users ─────────────────────────────────────────────────────────────────
    op.create_table(
        "users",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("email", sa.String(160), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("role", user_role_enum, nullable=False),
        sa.Column("phone", sa.String(20), nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
    )
    op.create_unique_constraint("uq_users_email", "users", ["email"])
    op.create_index("idx_users_role", "users", ["role"])

    # ── patients ──────────────────────────────────────────────────────────────
    op.create_table(
        "patients",
        sa.Column(
            "user_id",
            sa.BigInteger,
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("cpf", sa.String(14), nullable=True),
        sa.Column("birth_date", sa.Date, nullable=True),
    )
    op.create_unique_constraint("uq_patients_cpf", "patients", ["cpf"])


def downgrade() -> None:
    op.drop_table("patients")
    op.drop_table("users")
    sa.Enum(name="user_role").drop(op.get_bind(), checkfirst=True)
