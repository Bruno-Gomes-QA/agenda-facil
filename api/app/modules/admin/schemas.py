import secrets
import string

from pydantic import BaseModel, Field

from app.modules.users.schemas import UserOut


class AdminPatientCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: str = Field(min_length=5, max_length=160)
    password: str | None = Field(default=None, min_length=6, max_length=128)
    phone: str | None = Field(default=None, max_length=20)
    cpf: str | None = Field(default=None, max_length=14)


class AdminPatientCreateResponse(BaseModel):
    user: UserOut
    generated_password: str | None = None


class AdminPatientUpdate(BaseModel):
    name: str | None = None
    phone: str | None = None
    is_active: bool | None = None


def generate_password(length: int = 10) -> str:
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))
