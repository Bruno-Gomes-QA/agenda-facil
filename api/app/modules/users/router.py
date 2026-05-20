from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, require_role
from app.core.security import create_access_token, verify_password
from .models import User, UserRole
from .schemas import LoginRequest, LoginResponse, PatientCreate, StaffCreate, UserOut
from . import service

# ── Routers ───────────────────────────────────────────────────────────────────

router = APIRouter(prefix="/users", tags=["users"])
auth_router = APIRouter(prefix="/auth", tags=["auth"])


# ── /users ────────────────────────────────────────────────────────────────────

@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register_patient(data: PatientCreate, db: Session = Depends(get_db)):
    """Cadastro público — cria apenas pacientes."""
    return service.create_patient(db, data)


@router.post("/staff", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register_staff(
    data: StaffCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_role(UserRole.recepcionista)),
):
    """Cria recepcionista ou médico. Apenas recepcionistas podem chamar."""
    return service.create_staff(db, data)


@router.get("/{user_id}", response_model=UserOut)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Detalhe do usuário. Próprio usuário ou recepcionista."""
    if current_user.role != UserRole.recepcionista and current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permissão insuficiente")
    return service.get_user_by_id(db, user_id)


# ── /auth ─────────────────────────────────────────────────────────────────────

@auth_router.post("/login", response_model=LoginResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    """Login para todos os papéis. Retorna JWT Bearer."""
    user = service.get_user_by_email(db, data.email)
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Conta desativada. Entre em contato com a recepção.",
        )
    token = create_access_token(subject=user.id, role=user.role.value)
    return LoginResponse(
        access_token=token,
        user=UserOut.model_validate(user),
    )


@auth_router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    """Perfil do usuário autenticado."""
    return UserOut.model_validate(current_user)


@auth_router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(_: User = Depends(get_current_user)):
    """Logout stateless — o cliente deve descartar o token."""
    return None
