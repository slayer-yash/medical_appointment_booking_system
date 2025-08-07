
from pydantic import BaseModel
from uuid import UUID

from app.schemas.doctor_slots import AvailableSlotResponseSchema
from app.schemas.user import UserResponseSchema

class AvailableDoctorResponseSchema(BaseModel):
    user_id: UUID
    speciality: str
    available_slots: list[AvailableSlotResponseSchema]

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True


class DoctorResponseSchema(BaseModel):
    id: UUID
    user_id: UUID
    speciality: str
    user: UserResponseSchema

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True
    