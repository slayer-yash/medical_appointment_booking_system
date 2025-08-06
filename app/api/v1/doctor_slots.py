
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, status
from app.services.logging_services import LoggingService
from app.services.doctor_slots_services import DoctorSlotServices
from app.schemas.api_response import APIResponse
from app.schemas.slots import AvailableSlotResponseSchema
from app.models.doctor_slots import DoctorSlot
from app.db.session import get_db
from typing import Annotated
from fastapi.security import OAuth2PasswordBearer



logger = LoggingService(__name__).get_logger()

class DoctorSlots():

    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
    router = APIRouter(prefix="/doctor_slots", tags=["Doctor Slots"])

    @router.get("/me", response_model=APIResponse[AvailableSlotResponseSchema])
    def get_current_doctor_available_slots (
        token: Annotated[str, Depends(oauth2_scheme)],
        db: Session = Depends(get_db)
    ):
        logger.info(f"GET/available_slots/me API accessed")
        logger.debug(f"Token: {token}")

        obj = DoctorSlotServices(db, DoctorSlot)
        records = obj.get_doctor_available_slots(token)

        return APIResponse[AvailableSlotResponseSchema](
            success=True,
            status_code=status.HTTP_200_OK,
            message="Current doctor available slots fetched",
            data=records
        )

        