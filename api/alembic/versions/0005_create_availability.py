"""create doctor availability rules

Revision ID: 0005
Revises: 0004
Create Date: 2026-05-20
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0005"
down_revision: Union[str, None] = "0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "doctor_availability_rules",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column(
            "doctor_id",
            sa.BigInteger,
            sa.ForeignKey("doctors.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("weekday", sa.SmallInteger, nullable=False),
        sa.Column("start_time", sa.Time, nullable=False),
        sa.Column("end_time", sa.Time, nullable=False),
        sa.CheckConstraint("weekday BETWEEN 0 AND 6", name="ck_avail_weekday"),
        sa.CheckConstraint("end_time > start_time", name="ck_avail_time_order"),
    )
    op.create_index("idx_avail_doctor", "doctor_availability_rules", ["doctor_id"])

    # ── Seed demo: seg-sex 08-12 e 14-18 para os 2 médicos demo ─────────────
    bind = op.get_bind()
    doctor_ids = [
        r[0]
        for r in bind.execute(sa.text("SELECT id FROM doctors ORDER BY id")).fetchall()
    ]
    if doctor_ids:
        rules = sa.table(
            "doctor_availability_rules",
            sa.column("doctor_id", sa.BigInteger),
            sa.column("weekday", sa.SmallInteger),
            sa.column("start_time", sa.Time),
            sa.column("end_time", sa.Time),
        )
        rows = []
        for did in doctor_ids:
            for wd in range(0, 5):  # seg-sex (0..4)
                rows.append({"doctor_id": did, "weekday": wd, "start_time": "08:00:00", "end_time": "12:00:00"})
                rows.append({"doctor_id": did, "weekday": wd, "start_time": "14:00:00", "end_time": "18:00:00"})
        op.bulk_insert(rules, rows)


def downgrade() -> None:
    op.drop_index("idx_avail_doctor", table_name="doctor_availability_rules")
    op.drop_table("doctor_availability_rules")
