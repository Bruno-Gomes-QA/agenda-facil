from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from .models import Specialty
from .schemas import SpecialtyCreate, SpecialtyUpdate


def _assert_name_unique(db: Session, name: str, exclude_id: int | None = None) -> None:
    normalized = name.strip().lower()
    q = db.query(Specialty).filter(func.lower(Specialty.name) == normalized)
    if exclude_id is not None:
        q = q.filter(Specialty.id != exclude_id)
    if q.first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Especialidade com esse nome já existe",
        )


def list_specialties(db: Session, include_inactive: bool = False) -> list[Specialty]:
    q = db.query(Specialty)
    if not include_inactive:
        q = q.filter(Specialty.is_active.is_(True))
    return q.order_by(Specialty.name.asc()).all()


def get_specialty(db: Session, specialty_id: int) -> Specialty:
    sp = db.query(Specialty).filter(Specialty.id == specialty_id).first()
    if not sp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Especialidade não encontrada")
    return sp


def create_specialty(db: Session, data: SpecialtyCreate) -> Specialty:
    _assert_name_unique(db, data.name)
    sp = Specialty(name=data.name.strip(), description=data.description)
    db.add(sp)
    db.commit()
    db.refresh(sp)
    return sp


def update_specialty(db: Session, specialty_id: int, data: SpecialtyUpdate) -> Specialty:
    sp = get_specialty(db, specialty_id)
    if data.name is not None and data.name.strip().lower() != sp.name.lower():
        _assert_name_unique(db, data.name, exclude_id=sp.id)
        sp.name = data.name.strip()
    if data.description is not None:
        sp.description = data.description
    if data.is_active is not None:
        if data.is_active is False:
            _assert_no_active_doctors(db, sp.id)
        sp.is_active = data.is_active
    db.commit()
    db.refresh(sp)
    return sp


def _assert_no_active_doctors(db: Session, specialty_id: int) -> None:
    # late import — doctors depende de specialties
    from app.modules.doctors.models import Doctor

    count = (
        db.query(Doctor)
        .filter(Doctor.specialty_id == specialty_id, Doctor.is_active.is_(True))
        .count()
    )
    if count > 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Não é possível inativar: há {count} médico(s) ativo(s) vinculado(s)",
        )


def deactivate_specialty(db: Session, specialty_id: int) -> Specialty:
    sp = get_specialty(db, specialty_id)
    if sp.is_active:
        _assert_no_active_doctors(db, sp.id)
        sp.is_active = False
        db.commit()
        db.refresh(sp)
    return sp
