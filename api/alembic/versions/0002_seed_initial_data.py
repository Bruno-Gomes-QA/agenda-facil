"""seed initial users and demo data

Revision ID: 0002
Revises: 0001
Create Date: 2026-05-19

Seeds criados nesta migration (ambiente de desenvolvimento/QA):
  admin@agendafacil.local / admin123  → recepcionista
  dr.house@agendafacil.local / house123 → medico
  dra.grey@agendafacil.local / grey123 → medico
  paciente@agendafacil.local / paciente123 → paciente
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from passlib.context import CryptContext

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

_SEED_EMAILS = (
    "admin@agendafacil.local",
    "dr.house@agendafacil.local",
    "dra.grey@agendafacil.local",
    "paciente@agendafacil.local",
)


def upgrade() -> None:
    users_table = sa.table(
        "users",
        sa.column("name", sa.String),
        sa.column("email", sa.String),
        sa.column("password_hash", sa.String),
        sa.column("role", sa.String),
        sa.column("phone", sa.String),
        sa.column("is_active", sa.Boolean),
    )

    op.bulk_insert(
        users_table,
        [
            {
                "name": "Admin Recepcionista",
                "email": "admin@agendafacil.local",
                "password_hash": _pwd.hash("admin123"),
                "role": "recepcionista",
                "phone": None,
                "is_active": True,
            },
            {
                "name": "Dr. House",
                "email": "dr.house@agendafacil.local",
                "password_hash": _pwd.hash("house123"),
                "role": "medico",
                "phone": None,
                "is_active": True,
            },
            {
                "name": "Dra. Grey",
                "email": "dra.grey@agendafacil.local",
                "password_hash": _pwd.hash("grey123"),
                "role": "medico",
                "phone": None,
                "is_active": True,
            },
            {
                "name": "Paciente Demo",
                "email": "paciente@agendafacil.local",
                "password_hash": _pwd.hash("paciente123"),
                "role": "paciente",
                "phone": "(11) 99999-9999",
                "is_active": True,
            },
        ],
    )


def downgrade() -> None:
    emails = ", ".join(f"'{e}'" for e in _SEED_EMAILS)
    op.execute(f"DELETE FROM users WHERE email IN ({emails})")  # noqa: S608
