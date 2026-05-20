from datetime import date, datetime, time, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.modules.doctors.service import get_doctor

from .models import DoctorAvailabilityRule
from .schemas import AvailabilityRuleCreate, AvailabilityResponse, AvailabilitySlot

SLOT_MIN = 30
LEAD_TIME_MIN = 60
MAX_FUTURE_DAYS = 60


def list_rules(db: Session, doctor_id: int) -> list[DoctorAvailabilityRule]:
    return (
        db.query(DoctorAvailabilityRule)
        .filter(DoctorAvailabilityRule.doctor_id == doctor_id)
        .order_by(DoctorAvailabilityRule.weekday.asc(), DoctorAvailabilityRule.start_time.asc())
        .all()
    )


def _overlaps(a_start: time, a_end: time, b_start: time, b_end: time) -> bool:
    return a_start < b_end and b_start < a_end


def create_rule(db: Session, doctor_id: int, data: AvailabilityRuleCreate) -> DoctorAvailabilityRule:
    get_doctor(db, doctor_id)
    if data.end_time <= data.start_time:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Horário final deve ser maior que inicial",
        )
    existing = (
        db.query(DoctorAvailabilityRule)
        .filter(
            DoctorAvailabilityRule.doctor_id == doctor_id,
            DoctorAvailabilityRule.weekday == data.weekday,
        )
        .all()
    )
    for r in existing:
        if _overlaps(data.start_time, data.end_time, r.start_time, r.end_time):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Janela sobrepõe outra existente no mesmo dia",
            )
    rule = DoctorAvailabilityRule(
        doctor_id=doctor_id,
        weekday=data.weekday,
        start_time=data.start_time,
        end_time=data.end_time,
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule


def delete_rule(db: Session, doctor_id: int, rule_id: int) -> None:
    rule = (
        db.query(DoctorAvailabilityRule)
        .filter(DoctorAvailabilityRule.id == rule_id, DoctorAvailabilityRule.doctor_id == doctor_id)
        .first()
    )
    if not rule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Regra não encontrada")
    db.delete(rule)
    db.commit()


def _slot_times_for_rule(d: date, start: time, end: time) -> list[datetime]:
    start_dt = datetime.combine(d, start, tzinfo=timezone.utc)
    end_dt = datetime.combine(d, end, tzinfo=timezone.utc)
    out: list[datetime] = []
    cur = start_dt
    while cur + timedelta(minutes=SLOT_MIN) <= end_dt:
        out.append(cur)
        cur += timedelta(minutes=SLOT_MIN)
    return out


def list_slots(db: Session, doctor_id: int, target: date) -> AvailabilityResponse:
    get_doctor(db, doctor_id)

    now = datetime.now(timezone.utc)
    if (target - now.date()).days > MAX_FUTURE_DAYS:
        return AvailabilityResponse(doctor_id=doctor_id, date=target, slots=[])

    rules = (
        db.query(DoctorAvailabilityRule)
        .filter(
            DoctorAvailabilityRule.doctor_id == doctor_id,
            DoctorAvailabilityRule.weekday == target.weekday(),
        )
        .all()
    )

    candidate: list[datetime] = []
    for r in rules:
        candidate.extend(_slot_times_for_rule(target, r.start_time, r.end_time))

    # Remove ocupados
    from app.modules.appointments.models import Appointment, AppointmentStatus

    busy_rows = (
        db.query(Appointment.scheduled_at)
        .filter(
            Appointment.doctor_id == doctor_id,
            Appointment.status == AppointmentStatus.agendada,
            Appointment.scheduled_at >= datetime.combine(target, time(0, 0), tzinfo=timezone.utc),
            Appointment.scheduled_at < datetime.combine(target + timedelta(days=1), time(0, 0), tzinfo=timezone.utc),
        )
        .all()
    )
    busy = {row[0] for row in busy_rows}

    min_dt = now + timedelta(minutes=LEAD_TIME_MIN)
    free = [s for s in candidate if s not in busy and s >= min_dt]
    free.sort()
    return AvailabilityResponse(
        doctor_id=doctor_id,
        date=target,
        slots=[AvailabilitySlot(datetime=s) for s in free],
    )
