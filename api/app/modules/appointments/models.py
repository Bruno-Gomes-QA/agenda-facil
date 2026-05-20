import enum
from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Enum as SAEnum,
    ForeignKey,
    Index,
    SmallInteger,
    String,
    Text,
    TIMESTAMP,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class AppointmentStatus(str, enum.Enum):
    agendada = "agendada"
    cancelada = "cancelada"
    realizada = "realizada"
    no_show = "no_show"


class Appointment(Base):
    __tablename__ = "appointments"
    __table_args__ = (
        Index("idx_appt_patient", "patient_id"),
        Index("idx_appt_doctor_date", "doctor_id", "scheduled_at"),
        Index("idx_appt_status", "status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    patient_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    doctor_id: Mapped[int] = mapped_column(
        ForeignKey("doctors.id", ondelete="RESTRICT"), nullable=False
    )
    scheduled_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False)
    duration_min: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=30, server_default="30")
    status: Mapped[AppointmentStatus] = mapped_column(
        SAEnum(AppointmentStatus, name="appointment_status", create_constraint=False),
        nullable=False,
        default=AppointmentStatus.agendada,
        server_default=text("'agendada'"),
    )
    reason: Mapped[str | None] = mapped_column(String(255))
    doctor_notes: Mapped[str | None] = mapped_column(Text)
    created_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    rescheduled_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True))
    cancelled_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True))
    cancelled_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=text("NOW()"), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=text("NOW()"), nullable=False
    )

    patient = relationship("User", foreign_keys=[patient_id], lazy="joined")
    doctor = relationship("Doctor", lazy="joined")


class AppointmentHistory(Base):
    __tablename__ = "appointment_history"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    appointment_id: Mapped[int] = mapped_column(
        ForeignKey("appointments.id", ondelete="CASCADE"), nullable=False
    )
    changed_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    from_status: Mapped[AppointmentStatus | None] = mapped_column(
        SAEnum(AppointmentStatus, name="appointment_status", create_constraint=False, create_type=False)
    )
    to_status: Mapped[AppointmentStatus | None] = mapped_column(
        SAEnum(AppointmentStatus, name="appointment_status", create_constraint=False, create_type=False)
    )
    note: Mapped[str | None] = mapped_column(String(255))
    changed_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=text("NOW()"), nullable=False
    )
