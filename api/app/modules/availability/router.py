from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.modules.doctors.service import get_doctor, get_doctor_by_user
from app.modules.users.models import User, UserRole

from . import service
from .schemas import AvailabilityResponse, AvailabilityRuleCreate, AvailabilityRuleOut

router = APIRouter(prefix="/doctors", tags=["availability"])


def _assert_can_manage_rules(current: User, doctor_id: int, db: Session) -> None:
    if current.role == UserRole.recepcionista:
        return
    if current.role == UserRole.medico:
        own = get_doctor_by_user(db, current.id)
        if own.id == doctor_id:
            return
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permissão insuficiente")


@router.get("/{doctor_id}/availability-rules", response_model=list[AvailabilityRuleOut])
def list_rules(
    doctor_id: int,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    _assert_can_manage_rules(current, doctor_id, db)
    return service.list_rules(db, doctor_id)


@router.post(
    "/{doctor_id}/availability-rules",
    response_model=AvailabilityRuleOut,
    status_code=status.HTTP_201_CREATED,
)
def create_rule(
    doctor_id: int,
    data: AvailabilityRuleCreate,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    _assert_can_manage_rules(current, doctor_id, db)
    return service.create_rule(db, doctor_id, data)


@router.delete(
    "/{doctor_id}/availability-rules/{rule_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_rule(
    doctor_id: int,
    rule_id: int,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    _assert_can_manage_rules(current, doctor_id, db)
    service.delete_rule(db, doctor_id, rule_id)
    return None


@router.get("/{doctor_id}/availability", response_model=AvailabilityResponse)
def get_availability(
    doctor_id: int,
    target: date = Query(..., alias="date"),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    # garante que médico existe
    get_doctor(db, doctor_id)
    return service.list_slots(db, doctor_id, target)
