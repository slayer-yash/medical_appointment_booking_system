
from pydantic import BaseModel
from uuid import UUID
from app.schemas.user import UserResponseSchema

class PatientResponseSchema(BaseModel):
    id: UUID
    user_id: UUID
    user: UserResponseSchema

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True