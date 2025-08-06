
from pydantic import BaseModel, EmailStr, Field, field_validator
from uuid import UUID
from fastapi import Form, HTTPException, status
import string
from typing import Optional
import re
from datetime import datetime


class AvailableSlotResponseSchema(BaseModel):
    id: UUID
    start_time: datetime
    end_time: datetime
    is_booked: bool
    notes: Optional[str] = None
        
    
    class Config:
        from_attributes = True
        arbitrary_types_allowed = True

class SlotUpdateSchema(BaseModel):
    is_booked: bool
    notes: Optional[str] = None


