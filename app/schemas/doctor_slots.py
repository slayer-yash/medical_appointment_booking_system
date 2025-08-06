
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class AvailableSlotResponseSchema(BaseModel):
    doctor_id: UUID
    start_time: datetime
    end_time: datetime

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True