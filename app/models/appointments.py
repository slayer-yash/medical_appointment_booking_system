from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Boolean
from sqlalchemy.orm import relationship
from app.models.base_model import BaseModel
from sqlalchemy.dialects.postgresql import UUID

class Appointment(BaseModel):
    __tablename__ = "appointments"
    doctor_id = Column(UUID, ForeignKey("doctors.id", ondelete="CASCADE"))
    patient_id = Column(UUID, ForeignKey("patients.id", ondelete="CASCADE"))
    slot_id = Column(UUID, ForeignKey("doctor_slots.id", ondelete="CASCADE"))
    status = Column(String, nullable=False)
    is_mail_sent = Column(Boolean, default=False)
    created_by = Column(UUID, ForeignKey("users.id", ondelete="CASCADE"))
    
    doctor = relationship("Doctor", back_populates="appointments", uselist=False)
    patient = relationship("Patient", back_populates="appointments", uselist=False)
    slot = relationship("DoctorSlot", back_populates="appointment", uselist=False)

    