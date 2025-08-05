from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Boolean
from sqlalchemy.orm import relationship
from app.models.base_model import BaseModel
from sqlalchemy.dialects.postgresql import UUID

class DoctorSlot(BaseModel):
    __tablename__ = "doctor_slots"
    doctor_id = Column(UUID, ForeignKey("doctors.id"))
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    is_booked = Column(Boolean, default= False)
    
    doctor = relationship("Doctor", back_populates="available_slots")
    appointment = relationship("Appointment", back_populates="slot", uselist=False)

    