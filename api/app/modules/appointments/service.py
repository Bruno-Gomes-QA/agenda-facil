from datetime import date, datetime, time, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.modules.availability.service import LEAD_TIME_MIN, SLOT_MIN
from app.modules.doctors.service import get_doctor, to_public as doctor_to_public
from app.modules.users.models import User, UserRole
from app.modules.users.schemas import UserOut

from .models import Appointment, AppointmentHistory, AppointmentStatus
from .schemas import AppointmentCreate, AppointmentOut

CANCEL_LEAD_MIN = 30


# ── Helpers ───────────────────────────────────────────────────────────────────

def _validate_slot(db: Session, doctor_id: int, scheduled_at: datetime, *, bypass_lead: bool) -> None:
    if scheduled_at.tzinfo is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="scheduled_at deve incluir timezone",
        )
    scheduled_utc = scheduled_at.astimezone(timezone.utc)
    if scheduled_utc.minute % SLOT_MIN != 0 or scheduled_utc.second or scheduled_utc.microsecond:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Horário deve estar alinhado a blocos de {SLOT_MIN} minutos",
        )

    now = datetime.now(timezone.utc)
    if scheduled_utc <= now:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Não é possível agendar no passado",
        )
    if not bypass_lead and scheduled_utc < now + timedelta(minutes=LEAD_TIME_MIN):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Agendamento exige no mínimo {LEAD_TIME_MIN} minutos de antecedência",
        )

    # Janela do médico
    from app.modules.availability.models import DoctorAvailabilityRule

    weekday = scheduled_utc.weekday()
    target_time = scheduled_utc.time()
    end_time = (
        datetime.combine(date.today(), target_time) + timedelta(minutes=SLOT_MIN)
    ).time()

    rules = (
        db.query(DoctorAvailabilityRule)
        .filter(
            DoctorAvailabilityRule.doctor_id == doctor_id,
            DoctorAvailabilityRule.weekday == weekday,
        )
        .all()
    )

    def _within(r) -> bool:
        return r.start_time <= target_time and end_time <= r.end_time

    if not any(_within(r) for r in rules):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Horário fora da janela de atendimento do médico",
        )


def _assert_no_slot_conflict(db: Session, doctor_id: int, scheduled_utc: datetime, exclude_id: int | None = None) -> None:
    q = db.query(Appointment).filter(
        Appointment.doctor_id == doctor_id,
        Appointment.scheduled_at == scheduled_utc,
        Appointment.status == AppointmentStatus.agendada,
    )
    if exclude_id is not None:
        q = q.filter(Appointment.id != exclude_id)
    if q.first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe consulta agendada para este horário",
        )


def _assert_patient_no_clash(db: Session, patient_id: int, scheduled_utc: datetime, exclude_id: int | None = None) -> None:
    q = db.query(Appointment).filter(
        Appointment.patient_id == patient_id,
        Appointment.scheduled_at == scheduled_utc,
        Appointment.status == AppointmentStatus.agendada,
    )
    if exclude_id is not None:
        q = q.filter(Appointment.id != exclude_id)
    if q.first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Paciente já tem consulta neste horário",
        )


def _log_history(db: Session, appt: Appointment, user_id: int | None, from_status, to_status, note: str | None = None) -> None:
    h = AppointmentHistory(
        appointment_id=appt.id,
        changed_by=user_id,
        from_status=from_status,
        to_status=to_status,
        note=note,
    )
    db.add(h)


# ── Public serialization ──────────────────────────────────────────────────────

def to_out(appt: Appointment, *, hide_notes: bool = False) -> AppointmentOut:
    return AppointmentOut(
        id=appt.id,
        patient=UserOut.model_validate(appt.patient),
        doctor=doctor_to_public(appt.doctor),
        scheduled_at=appt.scheduled_at,
        duration_min=appt.duration_min,
        status=appt.status.value,
        reason=appt.reason,
        created_at=appt.created_at,
        rescheduled_at=appt.rescheduled_at,
        cancelled_at=appt.cancelled_at,
        cancelled_by=appt.cancelled_by,
        created_by=appt.created_by,
        doctor_notes=None if hide_notes else appt.doctor_notes,
    )


# ── Operations ────────────────────────────────────────────────────────────────

def create_appointment(
    db: Session,
    *,
    patient_id: int,
    data: AppointmentCreate,
    created_by_id: int,
    bypass_lead: bool = False,
) -> Appointment:
    doctor = get_doctor(db, data.doctor_id)
    if not doctor.is_active:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Médico inativo")

    # Paciente precisa estar ativo
    patient = db.query(User).filter(User.id == patient_id).first()
    if not patient or not patient.is_active:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Paciente inativo ou inexistente")
    if patient.role != UserRole.paciente:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Usuário não é paciente")

    _validate_slot(db, data.doctor_id, data.scheduled_at, bypass_lead=bypass_lead)
    scheduled_utc = data.scheduled_at.astimezone(timezone.utc)
    _assert_no_slot_conflict(db, data.doctor_id, scheduled_utc)
    _assert_patient_no_clash(db, patient_id, scheduled_utc)

    appt = Appointment(
        patient_id=patient_id,
        doctor_id=data.doctor_id,
        scheduled_at=scheduled_utc,
        reason=data.reason,
        created_by=created_by_id,
        status=AppointmentStatus.agendada,
    )
    db.add(appt)
    db.flush()
    _log_history(db, appt, created_by_id, None, AppointmentStatus.agendada, "criada")
    db.commit()
    db.refresh(appt)
    return appt


def get_appointment(db: Session, appointment_id: int) -> Appointment:
    appt = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Consulta não encontrada")
    return appt


def list_my_appointments(
    db: Session,
    patient_id: int,
    *,
    status_filter: str | None = None,
    from_date: date | None = None,
    to_date: date | None = None,
) -> list[Appointment]:
    q = db.query(Appointment).filter(Appointment.patient_id == patient_id)
    if status_filter:
        q = q.filter(Appointment.status == AppointmentStatus(status_filter))
    if from_date:
        q = q.filter(Appointment.scheduled_at >= datetime.combine(from_date, time(0, 0), tzinfo=timezone.utc))
    if to_date:
        q = q.filter(Appointment.scheduled_at < datetime.combine(to_date + timedelta(days=1), time(0, 0), tzinfo=timezone.utc))
    return q.order_by(Appointment.scheduled_at.desc()).limit(200).all()


def list_all_appointments(
    db: Session,
    *,
    doctor_id: int | None = None,
    patient_id: int | None = None,
    status_filter: str | None = None,
    from_date: date | None = None,
    to_date: date | None = None,
) -> list[Appointment]:
    q = db.query(Appointment)
    if doctor_id:
        q = q.filter(Appointment.doctor_id == doctor_id)
    if patient_id:
        q = q.filter(Appointment.patient_id == patient_id)
    if status_filter:
        q = q.filter(Appointment.status == AppointmentStatus(status_filter))
    if from_date:
        q = q.filter(Appointment.scheduled_at >= datetime.combine(from_date, time(0, 0), tzinfo=timezone.utc))
    if to_date:
        q = q.filter(Appointment.scheduled_at < datetime.combine(to_date + timedelta(days=1), time(0, 0), tzinfo=timezone.utc))
    return q.order_by(Appointment.scheduled_at.asc()).limit(500).all()


def list_doctor_appointments(
    db: Session,
    doctor_id: int,
    *,
    target_date: date | None = None,
    from_date: date | None = None,
    to_date: date | None = None,
) -> list[Appointment]:
    q = db.query(Appointment).filter(Appointment.doctor_id == doctor_id)
    if target_date:
        from_date = target_date
        to_date = target_date
    if from_date:
        q = q.filter(Appointment.scheduled_at >= datetime.combine(from_date, time(0, 0), tzinfo=timezone.utc))
    if to_date:
        q = q.filter(Appointment.scheduled_at < datetime.combine(to_date + timedelta(days=1), time(0, 0), tzinfo=timezone.utc))
    return q.order_by(Appointment.scheduled_at.asc()).all()


def reschedule(
    db: Session,
    appt: Appointment,
    new_scheduled: datetime,
    *,
    actor_id: int,
    bypass_lead: bool = False,
) -> Appointment:
    if appt.status != AppointmentStatus.agendada:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Consulta não está agendada")
    _validate_slot(db, appt.doctor_id, new_scheduled, bypass_lead=bypass_lead)
    new_utc = new_scheduled.astimezone(timezone.utc)
    _assert_no_slot_conflict(db, appt.doctor_id, new_utc, exclude_id=appt.id)
    _assert_patient_no_clash(db, appt.patient_id, new_utc, exclude_id=appt.id)

    appt.scheduled_at = new_utc
    appt.rescheduled_at = datetime.now(timezone.utc)
    _log_history(db, appt, actor_id, AppointmentStatus.agendada, AppointmentStatus.agendada, "remarcada")
    db.commit()
    db.refresh(appt)
    return appt


def cancel(
    db: Session,
    appt: Appointment,
    *,
    actor_id: int,
    bypass_lead: bool = False,
) -> Appointment:
    if appt.status != AppointmentStatus.agendada:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Consulta não está agendada")
    now = datetime.now(timezone.utc)
    if not bypass_lead and appt.scheduled_at - now < timedelta(minutes=CANCEL_LEAD_MIN):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cancelamento exige no mínimo {CANCEL_LEAD_MIN} minutos de antecedência",
        )
    appt.status = AppointmentStatus.cancelada
    appt.cancelled_at = now
    appt.cancelled_by = actor_id
    _log_history(db, appt, actor_id, AppointmentStatus.agendada, AppointmentStatus.cancelada, "cancelada")
    db.commit()
    db.refresh(appt)
    return appt


def set_status(
    db: Session,
    appt: Appointment,
    new_status: str,
    *,
    actor_id: int,
) -> Appointment:
    if appt.status != AppointmentStatus.agendada:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Status final não pode ser alterado")
    target = AppointmentStatus(new_status)
    if target not in (AppointmentStatus.realizada, AppointmentStatus.no_show):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Status inválido")
    now = datetime.now(timezone.utc)
    if target == AppointmentStatus.no_show and now < appt.scheduled_at:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Não é possível marcar no_show antes do horário",
        )
    old = appt.status
    appt.status = target
    _log_history(db, appt, actor_id, old, target, "status atualizado")
    db.commit()
    db.refresh(appt)
    return appt


def set_notes(db: Session, appt: Appointment, notes: str, *, actor_id: int) -> Appointment:
    appt.doctor_notes = notes
    _log_history(db, appt, actor_id, appt.status, appt.status, "notas atualizadas")
    db.commit()
    db.refresh(appt)
    return appt


def list_history(db: Session, appointment_id: int) -> list[AppointmentHistory]:
    return (
        db.query(AppointmentHistory)
        .filter(AppointmentHistory.appointment_id == appointment_id)
        .order_by(AppointmentHistory.changed_at.asc())
        .all()
    )
