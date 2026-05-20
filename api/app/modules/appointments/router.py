from datetime import date

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, require_role
from app.modules.doctors.service import get_doctor_by_user
from app.modules.users.models import User, UserRole

from . import service
from .schemas import (
    AppointmentCreate,
    AppointmentCreateAsStaff,
    AppointmentHistoryOut,
    AppointmentNotesUpdate,
    AppointmentOut,
    AppointmentStatusUpdate,
    AppointmentUpdate,
)

router = APIRouter(prefix="/appointments", tags=["appointments"])


def _serialize(appt, *, current: User) -> AppointmentOut:
    hide = current.role == UserRole.paciente
    return service.to_out(appt, hide_notes=hide)


# ── /appointments (create + list staff) ──────────────────────────────────────

@router.post("", response_model=AppointmentOut, status_code=status.HTTP_201_CREATED)
def create_appointment(
    data: AppointmentCreate | AppointmentCreateAsStaff = Body(...),
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    if current.role == UserRole.recepcionista:
        if not isinstance(data, AppointmentCreateAsStaff) and not getattr(data, "patient_id", None):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="patient_id é obrigatório para recepcionista",
            )
        patient_id = data.patient_id  # type: ignore[union-attr]
        appt = service.create_appointment(
            db,
            patient_id=patient_id,
            data=AppointmentCreate(
                doctor_id=data.doctor_id,
                scheduled_at=data.scheduled_at,
                reason=data.reason,
            ),
            created_by_id=current.id,
            bypass_lead=True,
        )
    elif current.role == UserRole.paciente:
        appt = service.create_appointment(
            db,
            patient_id=current.id,
            data=AppointmentCreate(
                doctor_id=data.doctor_id,
                scheduled_at=data.scheduled_at,
                reason=data.reason,
            ),
            created_by_id=current.id,
            bypass_lead=False,
        )
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permissão insuficiente")
    return _serialize(appt, current=current)


@router.get("/me", response_model=list[AppointmentOut])
def list_mine(
    status_filter: str | None = Query(None, alias="status"),
    from_date: date | None = Query(None, alias="from"),
    to_date: date | None = Query(None, alias="to"),
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    if current.role != UserRole.paciente:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Apenas pacientes")
    items = service.list_my_appointments(
        db, current.id, status_filter=status_filter, from_date=from_date, to_date=to_date
    )
    return [_serialize(a, current=current) for a in items]


@router.get("", response_model=list[AppointmentOut])
def list_all(
    doctor_id: int | None = Query(None),
    patient_id: int | None = Query(None),
    status_filter: str | None = Query(None, alias="status"),
    from_date: date | None = Query(None, alias="from"),
    to_date: date | None = Query(None, alias="to"),
    db: Session = Depends(get_db),
    _: User = Depends(require_role(UserRole.recepcionista)),
):
    items = service.list_all_appointments(
        db,
        doctor_id=doctor_id,
        patient_id=patient_id,
        status_filter=status_filter,
        from_date=from_date,
        to_date=to_date,
    )
    return [service.to_out(a) for a in items]


# ── doctor's own agenda ──────────────────────────────────────────────────────

@router.get("/doctor/me", response_model=list[AppointmentOut])
def list_doctor_mine(
    target: date | None = Query(None, alias="date"),
    from_date: date | None = Query(None, alias="from"),
    to_date: date | None = Query(None, alias="to"),
    db: Session = Depends(get_db),
    current: User = Depends(require_role(UserRole.medico)),
):
    doctor = get_doctor_by_user(db, current.id)
    if target is None and from_date is None and to_date is None:
        target = date.today()
    items = service.list_doctor_appointments(
        db, doctor.id, target_date=target, from_date=from_date, to_date=to_date
    )
    return [service.to_out(a) for a in items]


# ── per-id endpoints ─────────────────────────────────────────────────────────

def _authorize_access(appt, current: User, db: Session) -> None:
    if current.role == UserRole.recepcionista:
        return
    if current.role == UserRole.paciente:
        if appt.patient_id != current.id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Consulta não encontrada")
        return
    if current.role == UserRole.medico:
        doctor = get_doctor_by_user(db, current.id)
        if appt.doctor_id != doctor.id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Consulta não encontrada")
        return


@router.get("/{appointment_id}", response_model=AppointmentOut)
def get_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    appt = service.get_appointment(db, appointment_id)
    _authorize_access(appt, current, db)
    return _serialize(appt, current=current)


@router.patch("/{appointment_id}", response_model=AppointmentOut)
def reschedule_appointment(
    appointment_id: int,
    data: AppointmentUpdate,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    appt = service.get_appointment(db, appointment_id)
    _authorize_access(appt, current, db)
    if current.role == UserRole.medico:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Médico não remarca")
    bypass = current.role == UserRole.recepcionista
    appt = service.reschedule(db, appt, data.scheduled_at, actor_id=current.id, bypass_lead=bypass)
    return _serialize(appt, current=current)


@router.delete("/{appointment_id}", response_model=AppointmentOut)
def cancel_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    appt = service.get_appointment(db, appointment_id)
    _authorize_access(appt, current, db)
    if current.role == UserRole.medico:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Médico não cancela")
    bypass = current.role == UserRole.recepcionista
    appt = service.cancel(db, appt, actor_id=current.id, bypass_lead=bypass)
    return _serialize(appt, current=current)


@router.patch("/{appointment_id}/status", response_model=AppointmentOut)
def update_status(
    appointment_id: int,
    data: AppointmentStatusUpdate,
    db: Session = Depends(get_db),
    current: User = Depends(require_role(UserRole.medico)),
):
    appt = service.get_appointment(db, appointment_id)
    _authorize_access(appt, current, db)
    appt = service.set_status(db, appt, data.status, actor_id=current.id)
    return service.to_out(appt)


@router.patch("/{appointment_id}/notes", response_model=AppointmentOut)
def update_notes(
    appointment_id: int,
    data: AppointmentNotesUpdate,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    if current.role not in (UserRole.medico, UserRole.recepcionista):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permissão insuficiente")
    appt = service.get_appointment(db, appointment_id)
    _authorize_access(appt, current, db)
    appt = service.set_notes(db, appt, data.doctor_notes, actor_id=current.id)
    return service.to_out(appt)


@router.get("/{appointment_id}/history", response_model=list[AppointmentHistoryOut])
def get_history(
    appointment_id: int,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    appt = service.get_appointment(db, appointment_id)
    _authorize_access(appt, current, db)
    return service.list_history(db, appointment_id)
