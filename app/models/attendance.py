from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Boolean, Date
from sqlalchemy.orm import relationship
from app.models.base_model import BaseModel
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime

class Attendance(BaseModel):
    __tablename__ = "attendances"
    user_id = Column(UUID, ForeignKey("users.id"))
    date = Column(Date, default=datetime.today())
    time_in = Column(DateTime)
    time_out = Column(DateTime)
    created_by = Column(UUID, ForeignKey("users.id", ondelete="CASCADE"))
    