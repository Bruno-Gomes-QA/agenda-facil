from fastapi import HTTPException, status
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.modules.specialties.service import get_specialty
from app.modules.users.models import User, UserRole
from app.modules.users.service import _assert_email_unique, _normalize_email

from .models import Doctor
from .schemas import DoctorCreate, DoctorOut, DoctorPublicOut, DoctorUpdate


def _to_public(doctor: Doctor) -> DoctorPublicOut:
    return DoctorPublicOut(
        id=doctor.id,
        name=doctor.user.name,
        crm=doctor.crm,
        bio=doctor.bio,
        is_active=doctor.is_active,
        specialty=doctor.specialty,  # type: ignore[arg-type]
    )


def _to_out(doctor: Doctor) -> DoctorOut:
    return DoctorOut(
        id=doctor.id,
        name=doctor.user.name,
        crm=doctor.crm,
        bio=doctor.bio,
        is_active=doctor.is_active,
        specialty=doctor.specialty,  # type: ignore[arg-type]
        email=doctor.user.email,
        phone=doctor.user.phone,
        user_id=doctor.user_id,
    )


def list_doctors(
    db: Session,
    specialty_id: int | None = None,
    search: str | None = None,
    include_inactive: bool = False,
) -> list[Doctor]:
    q = db.query(Doctor).join(User, Doctor.user_id == User.id)
    if not include_inactive:
        q = q.filter(Doctor.is_active.is_(True))
    if specialty_id is not None:
        q = q.filter(Doctor.specialty_id == specialty_id)
    if search:
        like = f"%{search.strip().lower()}%"
        q = q.filter(or_(func.lower(User.name).like(like), func.lower(Doctor.crm).like(like)))
    return q.order_by(User.name.asc()).all()


def get_doctor(db: Session, doctor_id: int) -> Doctor:
    d = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not d:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Médico não encontrado")
    return d


def get_doctor_by_user(db: Session, user_id: int) -> Doctor:
    d = db.query(Doctor).filter(Doctor.user_id == user_id).first()
    if not d:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Médico não encontrado")
    return d


def _assert_crm_unique(db: Session, crm: str) -> None:
    if db.query(Doctor).filter(Doctor.crm == crm).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="CRM já cadastrado")


def create_doctor(db: Session, data: DoctorCreate) -> Doctor:
    _assert_email_unique(db, data.email)
    _assert_crm_unique(db, data.crm)
    sp = get_specialty(db, data.specialty_id)
    if not sp.is_active:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Especialidade inativa")

    user = User(
        name=data.name.strip(),
        email=_normalize_email(data.email),
        password_hash=hash_password(data.password),
        role=UserRole.medico,
        phone=data.phone,
    )
    db.add(user)
    db.flush()
    doctor = Doctor(
        user_id=user.id,
        specialty_id=data.specialty_id,
        crm=data.crm,
        bio=data.bio,
    )
    db.add(doctor)
    db.commit()
    db.refresh(doctor)
    return doctor


def update_doctor(db: Session, doctor_id: int, data: DoctorUpdate) -> Doctor:
    doctor = get_doctor(db, doctor_id)
    if data.name is not None:
        doctor.user.name = data.name.strip()
    if data.phone is not None:
        doctor.user.phone = data.phone
    if data.specialty_id is not None and data.specialty_id != doctor.specialty_id:
        sp = get_specialty(db, data.specialty_id)
        if not sp.is_active:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Especialidade inativa"
            )
        doctor.specialty_id = data.specialty_id
    if data.bio is not None:
        doctor.bio = data.bio
    if data.is_active is not None:
        if data.is_active is False and doctor.is_active:
            _assert_no_future_appointments(db, doctor.id)
        doctor.is_active = data.is_active
        doctor.user.is_active = data.is_active
    db.commit()
    db.refresh(doctor)
    return doctor


def _assert_no_future_appointments(db: Session, doctor_id: int) -> None:
    from datetime import datetime, timezone

    from app.modules.appointments.models import Appointment, AppointmentStatus

    count = (
        db.query(Appointment)
        .filter(
            Appointment.doctor_id == doctor_id,
            Appointment.status == AppointmentStatus.agendada,
            Appointment.scheduled_at > datetime.now(timezone.utc),
        )
        .count()
    )
    if count > 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Médico possui {count} consulta(s) futura(s) agendada(s). Cancele-as antes.",
        )


def deactivate_doctor(db: Session, doctor_id: int) -> Doctor:
    doctor = get_doctor(db, doctor_id)
    if doctor.is_active:
        _assert_no_future_appointments(db, doctor.id)
        doctor.is_active = False
        doctor.user.is_active = False
        db.commit()
        db.refresh(doctor)
    return doctor


def to_public(doctor: Doctor) -> DoctorPublicOut:
    return _to_public(doctor)


def to_out(doctor: Doctor) -> DoctorOut:
    return _to_out(doctor)
