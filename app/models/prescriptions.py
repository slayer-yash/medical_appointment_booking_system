from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Boolean
from sqlalchemy.orm import relationship
from app.models.base_model import BaseModel
from sqlalchemy.dialects.postgresql import UUID

class Prescription(BaseModel):
    __tablename__ = "prescriptions"
    doctor_id = Column(UUID, ForeignKey("doctors.id", ondelete="CASCADE"))
    patient_id = Column(UUID, ForeignKey("patients.id", ondelete="CASCADE"))
    appointment_id = Column(UUID, ForeignKey("appointments.id", ondelete="CASCADE"))
    prescription_obj = Column(String)
    stored_on_cloud = Column(Boolean, default=False)
    doctor = relationship("Doctor", back_populates="prescriptions")
    patient = relationship("Patient", back_populates="prescriptions")
    created_by = Column(UUID, ForeignKey("users.id", ondelete="CASCADE"))