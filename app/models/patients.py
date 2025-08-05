from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.models.base_model import BaseModel
from sqlalchemy.dialects.postgresql import UUID

class Patient(BaseModel):
    __tablename__ = "patients"
    user_id = Column(UUID, ForeignKey("users.id", ondelete="CASCADE"))
    
    appointments = relationship("Appointment", back_populates="patient")
    prescriptions = relationship("Prescription", back_populates="patient")
    user = relationship("User", back_populates="patient", uselist=False, foreign_keys="Patient.user_id")