"""create appointments and history

Revision ID: 0006
Revises: 0005
Create Date: 2026-05-20
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0006"
down_revision: Union[str, None] = "0005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    appt_status_enum = sa.Enum(
        "agendada", "cancelada", "realizada", "no_show", name="appointment_status"
    )

    op.create_table(
        "appointments",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column(
            "patient_id",
            sa.BigInteger,
            sa.ForeignKey("users.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "doctor_id",
            sa.BigInteger,
            sa.ForeignKey("doctors.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("scheduled_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("duration_min", sa.SmallInteger, nullable=False, server_default=sa.text("30")),
        sa.Column(
            "status",
            appt_status_enum,
            nullable=False,
            server_default=sa.text("'agendada'"),
        ),
        sa.Column("reason", sa.String(255), nullable=True),
        sa.Column("doctor_notes", sa.Text, nullable=True),
        sa.Column("created_by", sa.BigInteger, sa.ForeignKey("users.id"), nullable=True),
        sa.Column("rescheduled_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("cancelled_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("cancelled_by", sa.BigInteger, sa.ForeignKey("users.id"), nullable=True),
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
    op.create_index("idx_appt_patient", "appointments", ["patient_id"])
    op.create_index("idx_appt_doctor_date", "appointments", ["doctor_id", "scheduled_at"])
    op.create_index("idx_appt_status", "appointments", ["status"])
    op.execute(
        "CREATE UNIQUE INDEX uniq_doctor_slot_active "
        "ON appointments(doctor_id, scheduled_at) WHERE status = 'agendada'"
    )

    op.create_table(
        "appointment_history",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column(
            "appointment_id",
            sa.BigInteger,
            sa.ForeignKey("appointments.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("changed_by", sa.BigInteger, sa.ForeignKey("users.id"), nullable=True),
        sa.Column(
            "from_status",
            sa.Enum(
                "agendada", "cancelada", "realizada", "no_show",
                name="appointment_status",
                create_type=False,
            ),
            nullable=True,
        ),
        sa.Column(
            "to_status",
            sa.Enum(
                "agendada", "cancelada", "realizada", "no_show",
                name="appointment_status",
                create_type=False,
            ),
            nullable=True,
        ),
        sa.Column("note", sa.String(255), nullable=True),
        sa.Column(
            "changed_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_table("appointment_history")
    op.execute("DROP INDEX IF EXISTS uniq_doctor_slot_active")
    op.drop_index("idx_appt_status", table_name="appointments")
    op.drop_index("idx_appt_doctor_date", table_name="appointments")
    op.drop_index("idx_appt_patient", table_name="appointments")
    op.drop_table("appointments")
    sa.Enum(name="appointment_status").drop(op.get_bind(), checkfirst=True)
