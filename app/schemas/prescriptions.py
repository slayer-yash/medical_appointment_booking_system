
from pydantic import BaseModel
from uuid import UUID
from app.schemas.doctor import DoctorResponseSchema
from app.schemas.patient import PatientResponseSchema

class PrescriptionResponseSchema(BaseModel):
    doctor_id: UUID
    patient_id: UUID
    appointment_id: UUID
    prescription_obj: str
    created_by: UUID
    doctor: DoctorResponseSchema
    patient: PatientResponseSchema

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True