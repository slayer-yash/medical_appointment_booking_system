
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional
from app.schemas.user import UserResponseSchema

class AttendanceResponseSchema(BaseModel):
    id: UUID
    user_id: UUID
    date: datetime
    time_in: datetime
    time_out: Optional[datetime] = None
    created_by: UUID
    user: UserResponseSchema

    class Config:
        from_attributes=True
        arbitrary_types_allowed = True