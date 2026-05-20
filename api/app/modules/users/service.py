from sqlalchemy import func
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.core.security import hash_password
from .models import User, UserRole, Patient
from .schemas import PatientCreate, StaffCreate


def _normalize_email(email: str) -> str:
    return email.lower().strip()


def _assert_email_unique(db: Session, email: str, exclude_id: int | None = None) -> None:
    normalized = _normalize_email(email)
    q = db.query(User).filter(func.lower(User.email) == normalized)
    if exclude_id is not None:
        q = q.filter(User.id != exclude_id)
    if q.first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email já cadastrado",
        )


def create_patient(db: Session, data: PatientCreate) -> User:
    _assert_email_unique(db, data.email)

    user = User(
        name=data.name.strip(),
        email=_normalize_email(data.email),
        password_hash=hash_password(data.password),
        role=UserRole.paciente,
        phone=data.phone,
    )
    db.add(user)
    db.flush()  # obtém user.id antes do commit

    if data.cpf or data.birth_date:
        patient = Patient(user_id=user.id, cpf=data.cpf, birth_date=data.birth_date)
        db.add(patient)

    db.commit()
    db.refresh(user)
    return user


def create_staff(db: Session, data: StaffCreate) -> User:
    _assert_email_unique(db, data.email)

    role = UserRole.recepcionista if data.role == "recepcionista" else UserRole.medico
    user = User(
        name=data.name.strip(),
        email=_normalize_email(data.email),
        password_hash=hash_password(data.password),
        role=role,
        phone=data.phone,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user_by_id(db: Session, user_id: int) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado",
        )
    return user


def get_user_by_email(db: Session, email: str) -> User | None:
    normalized = _normalize_email(email)
    return db.query(User).filter(func.lower(User.email) == normalized).first()
