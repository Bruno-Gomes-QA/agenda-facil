from pydantic import BaseModel, EmailStr, Field

from app.modules.specialties.schemas import SpecialtyOut


class DoctorCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)
    phone: str | None = Field(default=None, max_length=20)
    specialty_id: int
    crm: str = Field(pattern=r"^\d{4,6}-[A-Z]{2}$")
    bio: str | None = None


class DoctorUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)
    phone: str | None = Field(default=None, max_length=20)
    specialty_id: int | None = None
    bio: str | None = None
    is_active: bool | None = None


class DoctorPublicOut(BaseModel):
    id: int
    name: str
    crm: str
    bio: str | None
    is_active: bool
    specialty: SpecialtyOut

    model_config = {"from_attributes": True}


class DoctorOut(DoctorPublicOut):
    email: EmailStr
    phone: str | None
    user_id: int
