
from pydantic import BaseModel
from uuid import UUID
from app.schemas.doctor import DoctorResponseSchema
from app.schemas.user import UserResponseSchema
from app.schemas.slots import AvailableSlotResponseSchema

class AppointmentResponseSchema(BaseModel):
    doctor_id: UUID
    patient_id: UUID
    slot_id: UUID
    status: str
    created_by: UUID
    doctor: DoctorResponseSchema
    patient: UserResponseSchema
    slot: AvailableSlotResponseSchema

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True
    