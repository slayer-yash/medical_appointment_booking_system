from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship, validates
from app.models.base_model import BaseModel
from sqlalchemy.dialects.postgresql import UUID

class Doctor(BaseModel):
    __tablename__ = "doctors"
    user_id = Column(UUID, ForeignKey("users.id", ondelete="CASCADE"))
    speciality = Column(String)
    
    appointments = relationship("Appointment", back_populates="doctor")
    prescriptions = relationship("Prescription", back_populates="doctor")
    available_slots = relationship("DoctorSlot", back_populates="doctor")
    user = relationship("User", back_populates="doctor", uselist=False, foreign_keys="Doctor.user_id")

