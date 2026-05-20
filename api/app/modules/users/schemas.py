from datetime import date
from typing import Literal

from pydantic import BaseModel, EmailStr, Field


# ── Entrada ───────────────────────────────────────────────────────────────────

class PatientCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)
    phone: str | None = Field(default=None, max_length=20)
    cpf: str | None = Field(default=None, max_length=14)
    birth_date: date | None = None


class StaffCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)
    role: Literal["recepcionista", "medico"]
    phone: str | None = Field(default=None, max_length=20)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# ── Saída ─────────────────────────────────────────────────────────────────────

class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: Literal["paciente", "recepcionista", "medico"]
    phone: str | None
    is_active: bool

    model_config = {"from_attributes": True}


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut
