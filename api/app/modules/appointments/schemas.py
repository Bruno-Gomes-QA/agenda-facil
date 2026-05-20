from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.modules.doctors.schemas import DoctorPublicOut
from app.modules.users.schemas import UserOut


class AppointmentCreate(BaseModel):
    doctor_id: int
    scheduled_at: datetime
    reason: str | None = Field(default=None, max_length=255)


class AppointmentCreateAsStaff(AppointmentCreate):
    patient_id: int


class AppointmentUpdate(BaseModel):
    scheduled_at: datetime


class AppointmentStatusUpdate(BaseModel):
    status: Literal["realizada", "no_show"]


class AppointmentNotesUpdate(BaseModel):
    doctor_notes: str = Field(max_length=4000)


class AppointmentOut(BaseModel):
    id: int
    patient: UserOut
    doctor: DoctorPublicOut
    scheduled_at: datetime
    duration_min: int
    status: Literal["agendada", "cancelada", "realizada", "no_show"]
    reason: str | None
    created_at: datetime
    rescheduled_at: datetime | None
    cancelled_at: datetime | None
    cancelled_by: int | None
    created_by: int | None
    doctor_notes: str | None = None  # filtrado para paciente

    model_config = {"from_attributes": True}


class AppointmentHistoryOut(BaseModel):
    id: int
    appointment_id: int
    changed_by: int | None
    from_status: str | None
    to_status: str | None
    note: str | None
    changed_at: datetime

    model_config = {"from_attributes": True}
