"""create doctors and seed demo

Revision ID: 0004
Revises: 0003
Create Date: 2026-05-20
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0004"
down_revision: Union[str, None] = "0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "doctors",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column(
            "user_id",
            sa.BigInteger,
            sa.ForeignKey("users.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "specialty_id",
            sa.BigInteger,
            sa.ForeignKey("specialties.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("crm", sa.String(20), nullable=False),
        sa.Column("bio", sa.Text, nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.UniqueConstraint("user_id", name="uq_doctors_user_id"),
        sa.UniqueConstraint("crm", name="uq_doctors_crm"),
    )
    op.create_index("idx_doctors_specialty", "doctors", ["specialty_id"])

    # ── Seed demo: liga dr.house → Clínico Geral, dra.grey → Cardiologia ────
    bind = op.get_bind()
    rows = bind.execute(
        sa.text(
            "SELECT email, id FROM users "
            "WHERE email IN ('dr.house@agendafacil.local', 'dra.grey@agendafacil.local')"
        )
    ).fetchall()
    user_by_email = {r[0]: r[1] for r in rows}

    spec_rows = bind.execute(
        sa.text("SELECT name, id FROM specialties WHERE name IN ('Clínico Geral', 'Cardiologia')")
    ).fetchall()
    spec_by_name = {r[0]: r[1] for r in spec_rows}

    doctor_seed = []
    if "dr.house@agendafacil.local" in user_by_email and "Clínico Geral" in spec_by_name:
        doctor_seed.append(
            {
                "user_id": user_by_email["dr.house@agendafacil.local"],
                "specialty_id": spec_by_name["Clínico Geral"],
                "crm": "12345-SP",
                "bio": "Médico especialista em diagnósticos complexos.",
                "is_active": True,
            }
        )
    if "dra.grey@agendafacil.local" in user_by_email and "Cardiologia" in spec_by_name:
        doctor_seed.append(
            {
                "user_id": user_by_email["dra.grey@agendafacil.local"],
                "specialty_id": spec_by_name["Cardiologia"],
                "crm": "67890-SP",
                "bio": "Cardiologista experiente.",
                "is_active": True,
            }
        )
    if doctor_seed:
        doctors = sa.table(
            "doctors",
            sa.column("user_id", sa.BigInteger),
            sa.column("specialty_id", sa.BigInteger),
            sa.column("crm", sa.String),
            sa.column("bio", sa.Text),
            sa.column("is_active", sa.Boolean),
        )
        op.bulk_insert(doctors, doctor_seed)


def downgrade() -> None:
    op.drop_index("idx_doctors_specialty", table_name="doctors")
    op.drop_table("doctors")
