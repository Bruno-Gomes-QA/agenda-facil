from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, require_role
from app.modules.users.models import User, UserRole

from . import service
from .schemas import DoctorCreate, DoctorOut, DoctorPublicOut, DoctorUpdate

router = APIRouter(prefix="/doctors", tags=["doctors"])


@router.get("", response_model=list[DoctorPublicOut])
def list_doctors_public(
    specialty_id: int | None = Query(None),
    search: str | None = Query(None),
    include_inactive: bool = Query(False),
    db: Session = Depends(get_db),
):
    items = service.list_doctors(db, specialty_id, search, include_inactive)
    return [service.to_public(d) for d in items]


@router.get("/me", response_model=DoctorOut)
def get_my_doctor_profile(
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    """Retorna o perfil de médico do usuário autenticado (somente role medico)."""
    if current.role != UserRole.medico:
        from fastapi import HTTPException, status as st
        raise HTTPException(status_code=st.HTTP_403_FORBIDDEN, detail="Apenas médicos.")
    return service.to_out(service.get_doctor_by_user(db, current.id))


@router.get("/{doctor_id}", response_model=DoctorPublicOut)
def get_doctor_public(doctor_id: int, db: Session = Depends(get_db)):
    return service.to_public(service.get_doctor(db, doctor_id))


@router.post(
    "",
    response_model=DoctorOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role(UserRole.recepcionista))],
)
def create_doctor(data: DoctorCreate, db: Session = Depends(get_db)):
    return service.to_out(service.create_doctor(db, data))


@router.patch(
    "/{doctor_id}",
    response_model=DoctorOut,
    dependencies=[Depends(require_role(UserRole.recepcionista))],
)
def update_doctor(doctor_id: int, data: DoctorUpdate, db: Session = Depends(get_db)):
    return service.to_out(service.update_doctor(db, doctor_id, data))


@router.delete(
    "/{doctor_id}",
    response_model=DoctorOut,
    dependencies=[Depends(require_role(UserRole.recepcionista))],
)
def delete_doctor(doctor_id: int, db: Session = Depends(get_db)):
    return service.to_out(service.deactivate_doctor(db, doctor_id))


@router.get("/admin/{doctor_id}", response_model=DoctorOut)
def get_doctor_full(
    doctor_id: int,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    """Versão completa (com email) — qualquer usuário autenticado."""
    return service.to_out(service.get_doctor(db, doctor_id))
