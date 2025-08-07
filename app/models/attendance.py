from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Boolean, Date
from sqlalchemy.orm import relationship
from app.models.base_model import BaseModel
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import pytz

ist = pytz.timezone('Asia/Kolkata')

class Attendance(BaseModel):
    __tablename__ = "attendances"
    user_id = Column(UUID, ForeignKey("users.id"))
    date = Column(Date, default=datetime.now(ist).date())
    time_in = Column(DateTime(timezone=True), default=datetime.now(ist))
    time_out = Column(DateTime(timezone=True), nullable=True)
    created_by = Column(UUID, ForeignKey("users.id", ondelete="CASCADE"))
    user = relationship("User", foreign_keys="attendances.user_id", back_populates="attendances", uselist=False)
    