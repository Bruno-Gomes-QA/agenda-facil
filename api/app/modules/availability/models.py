from datetime import time

from sqlalchemy import CheckConstraint, ForeignKey, SmallInteger, Time
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class DoctorAvailabilityRule(Base):
    __tablename__ = "doctor_availability_rules"
    __table_args__ = (
        CheckConstraint("weekday BETWEEN 0 AND 6", name="ck_avail_weekday"),
        CheckConstraint("end_time > start_time", name="ck_avail_time_order"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    doctor_id: Mapped[int] = mapped_column(
        ForeignKey("doctors.id", ondelete="CASCADE"), nullable=False, index=True
    )
    weekday: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
