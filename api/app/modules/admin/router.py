from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_role
from app.core.security import hash_password
from app.modules.users.models import Patient, User, UserRole
from app.modules.users.schemas import UserOut
from app.modules.users.service import _assert_email_unique, _normalize_email

from .schemas import (
    AdminPatientCreate,
    AdminPatientCreateResponse,
    AdminPatientUpdate,
    generate_password,
)

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(require_role(UserRole.recepcionista))],
)


@router.post("/patients", response_model=AdminPatientCreateResponse, status_code=status.HTTP_201_CREATED)
def create_patient(data: AdminPatientCreate, db: Session = Depends(get_db)):
    _assert_email_unique(db, data.email)
    generated: str | None = None
    password = data.password
    if not password:
        password = generate_password()
        generated = password

    user = User(
        name=data.name.strip(),
        email=_normalize_email(data.email),
        password_hash=hash_password(password),
        role=UserRole.paciente,
        phone=data.phone,
    )
    db.add(user)
    db.flush()
    if data.cpf:
        db.add(Patient(user_id=user.id, cpf=data.cpf))
    db.commit()
    db.refresh(user)
    return AdminPatientCreateResponse(user=UserOut.model_validate(user), generated_password=generated)


@router.get("/patients", response_model=list[UserOut])
def list_patients(
    search: str | None = Query(None),
    db: Session = Depends(get_db),
):
    q = db.query(User).filter(User.role == UserRole.paciente)
    if search:
        like = f"%{search.strip().lower()}%"
        q = q.outerjoin(Patient, Patient.user_id == User.id).filter(
            or_(
                func.lower(User.name).like(like),
                func.lower(User.email).like(like),
                func.lower(User.phone).like(like),
                func.lower(Patient.cpf).like(like),
            )
        )
    return q.order_by(User.name.asc()).limit(200).all()


@router.get("/patients/{user_id}", response_model=UserOut)
def get_patient(user_id: int, db: Session = Depends(get_db)):
    u = db.query(User).filter(User.id == user_id, User.role == UserRole.paciente).first()
    if not u:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paciente não encontrado")
    return u


@router.patch("/patients/{user_id}", response_model=UserOut)
def update_patient(user_id: int, data: AdminPatientUpdate, db: Session = Depends(get_db)):
    u = db.query(User).filter(User.id == user_id, User.role == UserRole.paciente).first()
    if not u:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paciente não encontrado")
    if data.name is not None:
        u.name = data.name.strip()
    if data.phone is not None:
        u.phone = data.phone
    if data.is_active is not None:
        u.is_active = data.is_active
    db.commit()
    db.refresh(u)
    return u
