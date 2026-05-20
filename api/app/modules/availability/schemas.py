from datetime import date, datetime, time

from pydantic import BaseModel, Field


class AvailabilityRuleCreate(BaseModel):
    weekday: int = Field(ge=0, le=6)
    start_time: time
    end_time: time


class AvailabilityRuleOut(BaseModel):
    id: int
    doctor_id: int
    weekday: int
    start_time: time
    end_time: time

    model_config = {"from_attributes": True}


class AvailabilitySlot(BaseModel):
    datetime: datetime
    available: bool = True


class AvailabilityResponse(BaseModel):
    doctor_id: int
    date: date
    slot_duration_min: int = 30
    slots: list[AvailabilitySlot]
