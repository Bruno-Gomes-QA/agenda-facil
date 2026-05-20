from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_role
from app.modules.users.models import UserRole

from . import service
from .schemas import SpecialtyCreate, SpecialtyOut, SpecialtyUpdate

router = APIRouter(prefix="/specialties", tags=["specialties"])


@router.get("", response_model=list[SpecialtyOut])
def list_(
    include_inactive: bool = Query(False),
    db: Session = Depends(get_db),
):
    return service.list_specialties(db, include_inactive=include_inactive)


@router.get("/{specialty_id}", response_model=SpecialtyOut)
def get(specialty_id: int, db: Session = Depends(get_db)):
    return service.get_specialty(db, specialty_id)


@router.post(
    "",
    response_model=SpecialtyOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role(UserRole.recepcionista))],
)
def create(data: SpecialtyCreate, db: Session = Depends(get_db)):
    return service.create_specialty(db, data)


@router.patch(
    "/{specialty_id}",
    response_model=SpecialtyOut,
    dependencies=[Depends(require_role(UserRole.recepcionista))],
)
def update(specialty_id: int, data: SpecialtyUpdate, db: Session = Depends(get_db)):
    return service.update_specialty(db, specialty_id, data)


@router.delete(
    "/{specialty_id}",
    response_model=SpecialtyOut,
    dependencies=[Depends(require_role(UserRole.recepcionista))],
)
def delete(specialty_id: int, db: Session = Depends(get_db)):
    return service.deactivate_specialty(db, specialty_id)
